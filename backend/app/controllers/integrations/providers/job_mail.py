"""
Job-email classification shared by Gmail and Outlook.

Turns a provider-agnostic message envelope into a normalized career event, so
both mailbox connectors feed the Application Pipeline through one code path
(spec §12/§13).  Classification is deterministic and explainable: every result
carries the signals that produced it, and a message we cannot classify with
confidence is returned as `None` rather than guessed into the pipeline.

Nothing here mutates a mailbox.  Read-only scopes are all either connector
requests, and no destructive action is possible through this module (spec §12).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# Ordered most-specific first: the first category whose pattern matches wins.
CATEGORY_PATTERNS: List[Tuple[str, List[str]]] = [
    (
        "OFFER",
        [
            r"\boffer letter\b",
            r"\bjob offer\b",
            r"\bwe(?:'re| are) (?:delighted|pleased|excited) to offer\b",
            r"\bextend(?:ing)? (?:you )?an offer\b",
            r"\boffer of employment\b",
        ],
    ),
    (
        "REJECTION",
        [
            r"\bnot (?:be )?(?:moving|proceeding|progressing) forward\b",
            r"\bdecided (?:to|not to) (?:move forward|proceed) with (?:other|another)\b",
            r"\bunfortunately\b.{0,80}\b(?:not|other candidates|unable)\b",
            r"\bwe(?:'ve| have) decided to pursue other candidates\b",
            r"\byour application (?:was|has been) unsuccessful\b",
            r"\bno longer under consideration\b",
            r"\bwill not be (?:progressing|continuing)\b",
        ],
    ),
    (
        "INTERVIEW_INVITATION",
        [
            r"\binterview (?:invitation|invite)\b",
            r"\b(?:schedule|book|set up|arrange)(?:\s+\w+){0,3}\s+(?:a\s+)?(?:call|interview|chat|screen)\b",
            r"\binvit(?:e|ing|ation) (?:you )?to (?:a|an) (?:interview|conversation|call)\b",
            r"\bphone screen\b",
            r"\btechnical interview\b",
            r"\bonsite (?:interview|loop)\b",
            r"\bavailability (?:for|to) (?:a )?(?:call|interview|chat)\b",
        ],
    ),
    (
        "ASSESSMENT_INVITATION",
        [
            r"\b(?:online|technical|coding|take[- ]home) (?:assessment|test|challenge|exercise)\b",
            r"\bcomplete (?:the |your )?(?:assessment|coding challenge|test)\b",
            r"\bhackerrank\b",
            r"\bcodility\b",
            r"\bcoderbyte\b",
            r"\bkarat\b",
            r"\bcodesignal\b",
        ],
    ),
    (
        "RECRUITER_OUTREACH",
        [
            r"\b(?:came across|found) your (?:profile|resume|github|linkedin)\b",
            r"\bwould you be (?:open|interested) (?:to|in)\b",
            r"\breach(?:ing)? out (?:about|regarding) (?:a|an) (?:role|opportunity|position)\b",
            r"\bexciting opportunity\b",
            r"\bhiring for\b",
            r"\bopportunity at\b",
        ],
    ),
    (
        "APPLICATION_RECEIVED",
        [
            r"\b(?:thank(?:s| you) for (?:your )?(?:applying|application|interest))\b",
            r"\b(?:we(?:'ve| have) received|received) your application\b",
            r"\byour application (?:to|for|has been received)\b",
            r"\bapplication (?:confirmation|submitted|received)\b",
            r"\bwe(?:'re| are) reviewing your application\b",
        ],
    ),
    (
        "STATUS_UPDATE",
        [
            r"\bapplication status\b",
            r"\bupdate on your (?:application|candidacy)\b",
            r"\bnext steps\b",
            r"\bmoving (?:you )?(?:forward|to the next)\b",
            r"\bstill (?:reviewing|considering)\b",
        ],
    ),
    (
        "FOLLOW_UP",
        [
            r"\bfollow(?:ing)?[- ]up\b",
            r"\bchecking in\b",
            r"\bgentle reminder\b",
            r"\bany update\b",
        ],
    ),
]

COMPILED: List[Tuple[str, List[re.Pattern]]] = [
    (category, [re.compile(p, re.IGNORECASE) for p in patterns])
    for category, patterns in CATEGORY_PATTERNS
]

#: Domains of applicant tracking systems and job boards. Mail from these is
#: career mail even when the wording is generic.
ATS_DOMAINS = {
    "greenhouse.io", "myworkday.com", "workday.com", "lever.co", "hire.lever.co",
    "smartrecruiters.com", "icims.com", "taleo.net", "successfactors.com",
    "ashbyhq.com", "jobvite.com", "bamboohr.com", "breezy.hr", "recruitee.com",
    "workable.com", "teamtailor.com", "avature.net", "eightfold.ai",
    "linkedin.com", "indeed.com", "glassdoor.com", "ziprecruiter.com",
    "hired.com", "wellfound.com", "angel.co", "otta.com", "dice.com",
    "naukri.com", "monster.com", "hackerrank.com", "codility.com",
    "codesignal.com", "karat.io", "notification.greenhouse.io",
}

#: A message must show at least one of these to be considered career mail at
#: all — this keeps newsletters and personal mail out of the pipeline.
CAREER_CONTEXT = re.compile(
    r"\b(?:application|applied|applying|candidate|candidacy|recruit(?:er|ing|ment)|"
    r"interview|hiring|role|position|job|offer|resume|cv|talent acquisition|"
    r"assessment|opening|vacancy)\b",
    re.IGNORECASE,
)

# "Software Engineer at Stripe", "Application for Backend Engineer"
ROLE_PATTERNS = [
    re.compile(r"(?:application|applying|applied|candidacy|interview)\s+for\s+(?:the\s+)?['\"]?([A-Z][\w+/&.,\- ]{2,60}?)['\"]?(?:\s+(?:at|@|with|position|role|opening)\b|[,.–—|]|$)"),
    re.compile(r"\b([A-Z][\w+/&.\- ]{2,60}?)\s+(?:role|position|opening|opportunity)\b"),
    re.compile(r"\byour\s+([A-Z][\w+/&.\- ]{2,60}?)\s+(?:application|interview)\b"),
]

COMPANY_PATTERNS = [
    re.compile(r"\b(?:at|@|with|from|join(?:ing)?)\s+([A-Z][\w&.\-]*(?:\s+[A-Z][\w&.\-]*){0,3})\b"),
]

NEXT_ACTION = {
    "APPLICATION_RECEIVED": "Wait for the recruiter's response",
    "RECRUITER_OUTREACH": "Reply to the recruiter",
    "ASSESSMENT_INVITATION": "Complete the assessment",
    "INTERVIEW_INVITATION": "Confirm interview availability",
    "STATUS_UPDATE": "Review the update and follow up if needed",
    "FOLLOW_UP": "Send a follow-up reply",
    "REJECTION": "Close out this application",
    "OFFER": "Review the offer terms",
}

#: Category -> Application.status transition (see app/models/jobs.py).
APPLICATION_STATUS = {
    "APPLICATION_RECEIVED": "APPLIED",
    "RECRUITER_OUTREACH": None,      # not necessarily an application yet
    "ASSESSMENT_INVITATION": "ASSESSMENT",
    "INTERVIEW_INVITATION": "INTERVIEWING",
    "STATUS_UPDATE": None,
    "FOLLOW_UP": None,
    "REJECTION": "REJECTED",
    "OFFER": "OFFER",
}

GENERIC_SENDER_LOCALPARTS = {
    "noreply", "no-reply", "donotreply", "do-not-reply", "notifications",
    "notification", "careers", "jobs", "recruiting", "recruitment", "talent",
    "hr", "hello", "info", "support", "mailer", "auto",
}


@dataclass
class MailMessage:
    """Provider-agnostic message envelope."""

    message_id: str
    thread_id: Optional[str]
    subject: str
    sender_name: Optional[str]
    sender_email: Optional[str]
    snippet: str
    received_at: Optional[datetime]
    label_ids: List[str] = field(default_factory=list)
    web_link: Optional[str] = None

    @property
    def sender_domain(self) -> Optional[str]:
        if not self.sender_email or "@" not in self.sender_email:
            return None
        return self.sender_email.rsplit("@", 1)[1].lower()


@dataclass
class JobMailEvent:
    """Normalized career event extracted from one message."""

    message_id: str
    thread_id: Optional[str]
    category: str
    confidence: float
    company: Optional[str]
    role: Optional[str]
    recruiter_name: Optional[str]
    recruiter_email: Optional[str]
    occurred_at: Optional[datetime]
    subject: str
    next_action: Optional[str]
    application_status: Optional[str]
    source: str
    signals: List[str]
    web_link: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "thread_id": self.thread_id,
            "category": self.category,
            "confidence": round(self.confidence, 2),
            "company": self.company,
            "role": self.role,
            "recruiter_name": self.recruiter_name,
            "recruiter_email": self.recruiter_email,
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
            "subject": self.subject,
            "next_action": self.next_action,
            "application_status": self.application_status,
            "source": self.source,
            "signals": self.signals,
            "web_link": self.web_link,
        }


def _is_ats_domain(domain: Optional[str]) -> bool:
    if not domain:
        return False
    return any(domain == d or domain.endswith(f".{d}") for d in ATS_DOMAINS)


def _extract_company(message: MailMessage) -> Optional[str]:
    """
    Prefer the sender's own domain — it is the most reliable company signal —
    and fall back to a capitalised phrase in the subject.
    """
    domain = message.sender_domain
    if domain and not _is_ats_domain(domain):
        label = domain.rsplit(".", 2)[0] if domain.count(".") > 1 else domain.split(".")[0]
        generic = {"gmail", "outlook", "hotmail", "yahoo", "icloud", "proton", "protonmail", "mail", "live", "msn"}
        if label and label.lower() not in generic:
            return label.replace("-", " ").title()

    # ATS mail usually names the company in the sender display name.
    if message.sender_name:
        cleaned = re.sub(
            r"\b(?:recruiting|recruitment|talent|careers?|hiring|team|no[- ]?reply|via\b.*)\b",
            "",
            message.sender_name,
            flags=re.IGNORECASE,
        ).strip(" -|,")
        if len(cleaned) >= 2 and not cleaned.lower().startswith("greenhouse"):
            return cleaned

    for pattern in COMPANY_PATTERNS:
        match = pattern.search(message.subject)
        if match:
            candidate = match.group(1).strip()
            if 2 <= len(candidate) <= 60:
                return candidate
    return None


def _extract_role(message: MailMessage) -> Optional[str]:
    for pattern in ROLE_PATTERNS:
        match = pattern.search(message.subject)
        if match:
            role = match.group(1).strip(" -|,–—")
            role = re.sub(r"\s{2,}", " ", role)
            if 2 <= len(role) <= 80:
                return role
    return None


def _recruiter(message: MailMessage) -> Tuple[Optional[str], Optional[str]]:
    """A generic mailbox is not a person; do not record it as a contact."""
    email = message.sender_email
    if not email:
        return None, None
    localpart = email.split("@", 1)[0].lower()
    if any(localpart.startswith(g) for g in GENERIC_SENDER_LOCALPARTS):
        return None, email
    name = message.sender_name
    if name and re.search(r"[A-Za-z]{2,}\s+[A-Za-z]{2,}", name):
        return name.strip(), email
    return None, email


def classify(message: MailMessage, source: str) -> Optional[JobMailEvent]:
    """
    Classify one message.  Returns None when the message is not career mail or
    the evidence is too weak — an unclassified message never enters the
    pipeline.
    """
    haystack = f"{message.subject}\n{message.snippet}"
    from_ats = _is_ats_domain(message.sender_domain)

    if not CAREER_CONTEXT.search(haystack) and not from_ats:
        return None

    signals: List[str] = []
    category: Optional[str] = None
    for name, patterns in COMPILED:
        for pattern in patterns:
            if pattern.search(haystack):
                category = category or name
                signals.append(f"{name}:{pattern.pattern[:40]}")
                break
        if category and len(signals) >= 3:
            break

    if not category:
        if from_ats:
            category = "STATUS_UPDATE"
            signals.append("ats_sender_domain")
        else:
            return None

    confidence = 0.5
    if from_ats:
        confidence += 0.25
        if "ats_sender_domain" not in signals:
            signals.append("ats_sender_domain")
    matched_for_category = sum(1 for s in signals if s.startswith(category))
    confidence += min(0.2, 0.1 * matched_for_category)
    if CAREER_CONTEXT.search(message.subject):
        confidence += 0.1
        signals.append("career_context_in_subject")
    confidence = min(confidence, 0.99)

    if confidence < 0.55:
        return None

    recruiter_name, recruiter_email = _recruiter(message)
    return JobMailEvent(
        message_id=message.message_id,
        thread_id=message.thread_id,
        category=category,
        confidence=confidence,
        company=_extract_company(message),
        role=_extract_role(message),
        recruiter_name=recruiter_name,
        recruiter_email=recruiter_email,
        occurred_at=message.received_at,
        subject=message.subject[:300],
        next_action=NEXT_ACTION.get(category),
        application_status=APPLICATION_STATUS.get(category),
        source=source,
        signals=signals[:6],
        web_link=message.web_link,
    )


def summarize(events: List[JobMailEvent]) -> Dict[str, Any]:
    """Aggregate counts for the sanitized sync summary shown in the UI."""
    counts: Dict[str, int] = {}
    for event in events:
        counts[event.category] = counts.get(event.category, 0) + 1
    latest = max((e.occurred_at for e in events if e.occurred_at), default=None)
    return {
        "job_emails_found": len(events),
        "by_category": counts,
        "companies_seen": sorted({e.company for e in events if e.company})[:25],
        "latest_event_at": latest.astimezone(timezone.utc).isoformat() if latest else None,
    }
