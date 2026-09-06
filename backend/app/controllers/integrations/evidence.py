"""
Evidence pipeline: normalized platform data → the rest of AI Career OS.

    External platform → connector → normalize → THIS MODULE → Skill Graph,
    Project Evidence, Application Pipeline → Career Analytics / AI Coach

Two things happen here:

1.  **Skill evidence.** Languages and topics observed on a platform become
    `Skill` rows.  Proficiency is *derived from the observed volume*, with the
    thresholds written down in `_proficiency_from_evidence` — never asserted.
    A language seen in one repository does not make somebody "Advanced".

2.  **Application pipeline.** Classified job emails become `Company`, `Job`,
    `Application`, `ApplicationEvent` and (for named humans) `Contact` rows.
    Existing applications are advanced, not duplicated, and a status is only
    ever moved forward through the funnel.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.jobs import Application, ApplicationEvent, Company, Contact, Job
from app.models.profile import Skill

from .normalize import NormalizedTelemetry

#: Skill rows we created get this category so they can be told apart from
#: user-entered skills and re-derived safely.
EVIDENCE_CATEGORY = "technical"

#: Ordered funnel. An email can move an application forward but never back.
STATUS_ORDER = [
    "SAVED",
    "APPLIED",
    "ASSESSMENT",
    "INTERVIEWING",
    "OFFER",
    "REJECTED",
    "WITHDRAWN",
]

#: Category → ApplicationEvent.event_type
EVENT_TYPES = {
    "APPLICATION_RECEIVED": "APPLICATION_CONFIRMED",
    "RECRUITER_OUTREACH": "RECRUITER_OUTREACH",
    "ASSESSMENT_INVITATION": "ASSESSMENT_INVITED",
    "INTERVIEW_INVITATION": "INTERVIEW_INVITED",
    "STATUS_UPDATE": "STATUS_UPDATE",
    "FOLLOW_UP": "FOLLOW_UP",
    "REJECTION": "REJECTED",
    "OFFER": "OFFER_RECEIVED",
}


#: Ordering used when deciding whether evidence may raise a proficiency label.
PROFICIENCY_LEVELS = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}


def _proficiency_from_evidence(signal: int) -> str:
    """
    Map observed volume to a proficiency label.

    The thresholds are deliberate and documented so the value is explainable:
      1        -> beginner       (seen once)
      2-4      -> intermediate   (recurring use)
      5-14     -> advanced       (sustained use across projects)
      15+      -> expert         (dominant, long-running use)
    """
    if signal >= 15:
        return "expert"
    if signal >= 5:
        return "advanced"
    if signal >= 2:
        return "intermediate"
    return "beginner"


def _skill_signals(telemetry: NormalizedTelemetry) -> Dict[str, int]:
    """Count how much evidence each skill name actually has."""
    signals: Dict[str, int] = {}

    def bump(name: Optional[str], amount: int = 1) -> None:
        if not name or not str(name).strip():
            return
        key = str(name).strip()[:100]
        signals[key] = signals.get(key, 0) + amount

    provider = telemetry.provider

    if provider == "github":
        for artifact in telemetry.artifacts:
            if artifact.artifact_type == "repository":
                bump(artifact.primary_language)
                for topic in (artifact.attributes or {}).get("topics") or []:
                    bump(str(topic).replace("-", " ").title())

    elif provider == "leetcode":
        # Topic strengths carry their own solved counts — real evidence volume.
        topics = telemetry.summary.get("topic_strengths") or {}
        for level in ("advanced", "intermediate", "fundamental"):
            for entry in topics.get(level) or []:
                topic = entry.get("topic")
                solved = entry.get("solved") or 0
                if topic and solved:
                    bump(topic, min(int(solved), 30))
        for language in telemetry.summary.get("languages") or []:
            name = language.get("language")
            solved = language.get("solved") or 0
            if name and solved:
                bump(name, min(int(solved), 30))

    elif provider == "huggingface":
        for artifact in telemetry.artifacts:
            tags = (artifact.attributes or {}).get("tags") or []
            pipeline_tag = (artifact.attributes or {}).get("pipeline_tag")
            if pipeline_tag:
                bump(str(pipeline_tag).replace("-", " ").title())
            for tag in tags:
                text = str(tag)
                # Framework/library tags are meaningful; bookkeeping tags are not.
                if text.lower() in {
                    "pytorch", "tensorflow", "jax", "transformers", "diffusers",
                    "safetensors", "onnx", "gguf", "peft", "sentence-transformers",
                }:
                    bump(text.title() if text.islower() else text)

    elif provider == "kaggle":
        for artifact in telemetry.artifacts:
            if artifact.artifact_type == "notebook" and artifact.primary_language:
                bump(artifact.primary_language)
        if telemetry.summary.get("datasets_count"):
            bump("Data Analysis", int(telemetry.summary["datasets_count"]))

    return signals


def apply_skill_evidence(db: Session, user_id: int, telemetry: NormalizedTelemetry) -> int:
    """
    Upsert skill rows from observed evidence.  Returns the number of rows
    written.  Never deletes a user's own skills and never downgrades a
    proficiency a user set themselves.
    """
    signals = _skill_signals(telemetry)
    if not signals:
        return 0

    written = 0
    for name, signal in signals.items():
        proficiency = _proficiency_from_evidence(signal)
        existing = db.execute(
            select(Skill).where(
                Skill.user_id == user_id,
                func.lower(Skill.name) == name.lower(),
            )
        ).scalars().first()

        if existing is None:
            db.add(
                Skill(
                    user_id=user_id,
                    name=name,
                    category=EVIDENCE_CATEGORY,
                    proficiency_level=proficiency,
                )
            )
            written += 1
            continue

        # Only ever raise a level; never overwrite a higher one a user set.
        current = PROFICIENCY_LEVELS.get((existing.proficiency_level or "").lower(), -1)
        candidate = PROFICIENCY_LEVELS.get(proficiency, 0)
        if candidate > current:
            existing.proficiency_level = proficiency
            written += 1
    return written


# --------------------------------------------------------------------------- #
# Application pipeline from mailbox events
# --------------------------------------------------------------------------- #

def _status_rank(status: Optional[str]) -> int:
    if not status:
        return -1
    try:
        return STATUS_ORDER.index(status.upper())
    except ValueError:
        return -1


def _get_or_create_company(db: Session, user_id: int, name: str) -> Company:
    existing = db.execute(
        select(Company).where(Company.user_id == user_id, func.lower(Company.name) == name.lower())
    ).scalars().first()
    if existing:
        return existing
    company = Company(user_id=user_id, name=name[:200])
    db.add(company)
    db.flush()
    return company


def _get_or_create_job(
    db: Session, user_id: int, company: Company, role: Optional[str], source: str
) -> Job:
    title = (role or "Role from email")[:200]
    existing = db.execute(
        select(Job).where(
            Job.user_id == user_id,
            Job.company_id == company.id,
            func.lower(Job.title) == title.lower(),
        )
    ).scalars().first()
    if existing:
        return existing
    job = Job(
        user_id=user_id,
        company_id=company.id,
        company_name=company.name,
        title=title,
        source=f"email:{source}",
    )
    db.add(job)
    db.flush()
    return job


def _get_or_create_contact(
    db: Session, user_id: int, company: Company, name: str, email: Optional[str]
) -> Contact:
    query = select(Contact).where(Contact.user_id == user_id)
    if email:
        query = query.where(func.lower(Contact.email) == email.lower())
    else:
        query = query.where(func.lower(Contact.name) == name.lower())
    existing = db.execute(query).scalars().first()
    if existing:
        return existing
    contact = Contact(
        user_id=user_id,
        company_id=company.id,
        name=name[:200],
        email=(email or None),
        designation="Recruiter",
    )
    db.add(contact)
    db.flush()
    return contact


def apply_mail_events(
    db: Session, user_id: int, events: List[Dict[str, Any]], source: str
) -> Dict[str, int]:
    """
    Fold classified job emails into the Application Pipeline.

    Idempotent: an `ApplicationEvent` whose description carries the message id
    is written once, so re-syncing the same mailbox does not duplicate history.
    """
    counters = {"companies": 0, "jobs": 0, "applications": 0, "events": 0, "contacts": 0}
    if not events:
        return counters

    for event in events:
        company_name = event.get("company")
        if not company_name:
            # Without a company we cannot place this in the pipeline honestly.
            continue

        message_id = event.get("message_id")
        marker = f"[msg:{message_id}]" if message_id else None
        if marker:
            already = db.execute(
                select(ApplicationEvent.id).where(ApplicationEvent.description.like(f"%{marker}%"))
            ).scalars().first()
            if already:
                continue

        company_before = db.execute(
            select(func.count(Company.id)).where(Company.user_id == user_id)
        ).scalar_one()
        company = _get_or_create_company(db, user_id, company_name)
        if db.execute(select(func.count(Company.id)).where(Company.user_id == user_id)).scalar_one() > company_before:
            counters["companies"] += 1

        job_before = db.execute(select(func.count(Job.id)).where(Job.user_id == user_id)).scalar_one()
        job = _get_or_create_job(db, user_id, company, event.get("role"), source)
        if db.execute(select(func.count(Job.id)).where(Job.user_id == user_id)).scalar_one() > job_before:
            counters["jobs"] += 1

        contact: Optional[Contact] = None
        if event.get("recruiter_name"):
            contacts_before = db.execute(
                select(func.count(Contact.id)).where(Contact.user_id == user_id)
            ).scalar_one()
            contact = _get_or_create_contact(
                db, user_id, company, event["recruiter_name"], event.get("recruiter_email")
            )
            if db.execute(
                select(func.count(Contact.id)).where(Contact.user_id == user_id)
            ).scalar_one() > contacts_before:
                counters["contacts"] += 1

        application = db.execute(
            select(Application).where(Application.user_id == user_id, Application.job_id == job.id)
        ).scalars().first()

        occurred_at = _to_naive(event.get("occurred_at"))
        target_status = event.get("application_status")

        if application is None:
            application = Application(
                user_id=user_id,
                job_id=job.id,
                status=target_status or "SAVED",
                applied_at=occurred_at if target_status == "APPLIED" else None,
                recruiter_contact_id=contact.id if contact else None,
                notes=f"Detected from {source} mail.",
            )
            db.add(application)
            db.flush()
            counters["applications"] += 1
        else:
            if target_status and _status_rank(target_status) > _status_rank(application.status):
                application.status = target_status
            if contact and not application.recruiter_contact_id:
                application.recruiter_contact_id = contact.id
            if target_status == "APPLIED" and not application.applied_at:
                application.applied_at = occurred_at

        description_bits = [event.get("subject") or event.get("category") or "Career email"]
        if event.get("next_action"):
            description_bits.append(f"Next: {event['next_action']}")
        description_bits.append(f"Source: {source}")
        if marker:
            description_bits.append(marker)

        db.add(
            ApplicationEvent(
                application_id=application.id,
                event_type=EVENT_TYPES.get(event.get("category", ""), "EMAIL_EVENT"),
                description=" | ".join(description_bits)[:2000],
                event_date=occurred_at or datetime.utcnow(),
            )
        )
        counters["events"] += 1

    return counters


def _to_naive(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    return parsed.astimezone(timezone.utc).replace(tzinfo=None) if parsed.tzinfo else parsed


def apply_all(
    db: Session, user_id: int, telemetry: NormalizedTelemetry
) -> Tuple[int, Dict[str, int]]:
    """
    Run every applicable evidence step for one sync.  Failures here must not
    fail the sync itself — the platform data is already stored — so they are
    logged and reported as zero evidence written.
    """
    skills_written = 0
    pipeline: Dict[str, int] = {}
    try:
        skills_written = apply_skill_evidence(db, user_id, telemetry)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Skill evidence step failed for %s: %r", telemetry.provider, exc)
    try:
        if telemetry.job_events:
            pipeline = apply_mail_events(db, user_id, telemetry.job_events, telemetry.provider)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Application pipeline step failed for %s: %r", telemetry.provider, exc)
    return skills_written, pipeline
