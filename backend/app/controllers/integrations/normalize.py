"""
Telemetry → normalized rows.

Each connector returns a provider-shaped dict.  This module converts that into
(a) `IntegrationMetric` rows, (b) `IntegrationArtifact` rows and (c) a small
sanitized summary for the UI.  It is pure: it builds plain dataclasses and never
touches the database or the network, which makes it directly testable.

Rule throughout: a value the provider did not give us is omitted, never
defaulted to zero (spec §25).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Metric keys copied verbatim from telemetry when present, with their unit.
_METRIC_SPECS: Dict[str, List[tuple]] = {
    "github": [
        ("repos_count", "count"),
        ("owned_repos_count", "count"),
        ("forks_count", "count"),
        ("total_stars", "count"),
        ("total_forks_received", "count"),
        ("recent_commits", "count"),
    ],
    "leetcode": [
        ("solved_total", "count"),
        ("solved_easy", "count"),
        ("solved_medium", "count"),
        ("solved_hard", "count"),
        ("total_accepted_submissions", "count"),
        ("contest_rating", "rating"),
        ("contests_attended", "count"),
        ("contest_global_ranking", "rank"),
        ("contest_top_percentage", "percent"),
        ("global_ranking", "rank"),
    ],
    "kaggle": [
        ("datasets_count", "count"),
        ("models_count", "count"),
        ("notebooks_count", "count"),
        ("total_dataset_downloads", "count"),
        ("total_dataset_votes", "count"),
        ("competitions_entered", "count"),
        ("medals", "count"),
    ],
    "huggingface": [
        ("models_count", "count"),
        ("datasets_count", "count"),
        ("spaces_count", "count"),
        ("total_model_downloads", "count"),
        ("total_model_likes", "count"),
        ("followers", "count"),
        ("upvotes_received", "count"),
        ("papers", "count"),
    ],
    "google": [
        ("messages_scanned", "count"),
        ("job_emails_found", "count"),
    ],
    "microsoft": [
        ("messages_scanned", "count"),
        ("job_emails_found", "count"),
    ],
}

#: Keys the UI needs; everything else stays out of API responses.
_SUMMARY_KEYS = {
    "username", "limitation_note", "data_source", "authenticated",
    "top_languages", "languages", "importable_data", "unavailable_data",
    "by_category", "scan_window_days", "latest_event_at", "identity_verified",
    "has_contest_history", "medals_note", "token_error", "full_name",
    "companies_seen", "activity_available",
}


@dataclass
class MetricRow:
    key: str
    value: Optional[float] = None
    text: Optional[str] = None
    unit: Optional[str] = None


@dataclass
class ArtifactRow:
    artifact_type: str
    external_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    primary_language: Optional[str] = None
    stars: Optional[int] = None
    forks: Optional[int] = None
    downloads: Optional[int] = None
    likes: Optional[int] = None
    occurred_at: Optional[datetime] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedTelemetry:
    provider: str
    metrics: List[MetricRow] = field(default_factory=list)
    artifacts: List[ArtifactRow] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    #: Classified job-mail events, forwarded to the Application Pipeline.
    job_events: List[Dict[str, Any]] = field(default_factory=list)


def _as_number(value: Any) -> Optional[float]:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _int_or_none(value: Any) -> Optional[int]:
    number = _as_number(value)
    return int(number) if number is not None else None


def _parse_dt(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value if value.tzinfo is None else value.astimezone(timezone.utc).replace(tzinfo=None)
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc).replace(tzinfo=None)
        except (OverflowError, OSError, ValueError):
            return None
    if isinstance(value, str) and value:
        candidate = value.strip()
        if candidate.isdigit():
            return _parse_dt(int(candidate))
        try:
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed.astimezone(timezone.utc).replace(tzinfo=None) if parsed.tzinfo else parsed
    return None


def normalize(provider: str, telemetry: Dict[str, Any]) -> NormalizedTelemetry:
    """Convert provider telemetry into metric and artifact rows plus a summary."""
    result = NormalizedTelemetry(provider=provider)
    if not isinstance(telemetry, dict):
        return result

    for key, unit in _METRIC_SPECS.get(provider, []):
        if key not in telemetry:
            continue
        number = _as_number(telemetry[key])
        if number is None:
            continue  # provider returned null -> record nothing, not zero
        result.metrics.append(MetricRow(key=key, value=number, unit=unit))

    handler = _ARTIFACT_HANDLERS.get(provider)
    if handler:
        handler(telemetry, result)

    result.summary = {k: v for k, v in telemetry.items() if k in _SUMMARY_KEYS and v is not None}
    result.summary.update({m.key: m.value for m in result.metrics})
    if provider == "leetcode":
        result.summary["topic_strengths"] = telemetry.get("topic_strengths") or {}
    return result


# ------------------------------------------------------------------ providers

def _github(telemetry: Dict[str, Any], out: NormalizedTelemetry) -> None:
    for repo in telemetry.get("recent_repos") or []:
        name = repo.get("full_name") or repo.get("name")
        if not name:
            continue
        out.artifacts.append(
            ArtifactRow(
                artifact_type="repository",
                external_id=str(name),
                title=repo.get("name"),
                description=repo.get("description"),
                url=repo.get("url"),
                primary_language=repo.get("language"),
                stars=_int_or_none(repo.get("stars")),
                forks=_int_or_none(repo.get("forks")),
                occurred_at=_parse_dt(repo.get("pushed_at")),
                attributes={"topics": (repo.get("topics") or [])[:12]},
            )
        )
    languages = telemetry.get("language_bytes") or {}
    if languages:
        out.metrics.append(
            MetricRow(key="languages_used", value=float(len(languages)), unit="count")
        )
    if telemetry.get("top_languages"):
        out.metrics.append(
            MetricRow(key="primary_language", text=str(telemetry["top_languages"][0])[:500])
        )
    orgs = telemetry.get("organizations") or []
    if orgs:
        out.metrics.append(MetricRow(key="organizations_count", value=float(len(orgs)), unit="count"))


def _leetcode(telemetry: Dict[str, Any], out: NormalizedTelemetry) -> None:
    for item in telemetry.get("recent_solved") or []:
        slug = item.get("slug")
        if not slug:
            continue
        out.artifacts.append(
            ArtifactRow(
                artifact_type="problem",
                external_id=str(slug),
                title=item.get("title"),
                url=f"https://leetcode.com/problems/{slug}/",
                occurred_at=_parse_dt(item.get("timestamp")),
            )
        )
    languages = telemetry.get("languages") or []
    if languages and languages[0].get("language"):
        out.metrics.append(MetricRow(key="primary_language", text=str(languages[0]["language"])[:500]))


def _kaggle(telemetry: Dict[str, Any], out: NormalizedTelemetry) -> None:
    for dataset in telemetry.get("datasets") or []:
        url = dataset.get("url")
        if not url:
            continue
        out.artifacts.append(
            ArtifactRow(
                artifact_type="dataset",
                external_id=str(url),
                title=dataset.get("title"),
                url=url,
                downloads=_int_or_none(dataset.get("downloads")),
                likes=_int_or_none(dataset.get("votes")),
                occurred_at=_parse_dt(dataset.get("updated")),
            )
        )
    for model in telemetry.get("models") or []:
        url = model.get("url")
        if not url:
            continue
        out.artifacts.append(
            ArtifactRow(
                artifact_type="model",
                external_id=str(url),
                title=model.get("title"),
                url=url,
                downloads=_int_or_none(model.get("downloads")),
            )
        )
    for notebook in telemetry.get("notebooks") or []:
        url = notebook.get("url")
        if not url:
            continue
        out.artifacts.append(
            ArtifactRow(
                artifact_type="notebook",
                external_id=str(url),
                title=notebook.get("title"),
                url=url,
                likes=_int_or_none(notebook.get("votes")),
                primary_language=notebook.get("language"),
            )
        )


def _huggingface(telemetry: Dict[str, Any], out: NormalizedTelemetry) -> None:
    for kind, artifact_type in (("models", "model"), ("datasets", "dataset"), ("spaces", "space")):
        for item in telemetry.get(kind) or []:
            repo_id = item.get("id")
            if not repo_id:
                continue
            out.artifacts.append(
                ArtifactRow(
                    artifact_type=artifact_type,
                    external_id=str(repo_id),
                    title=str(repo_id).split("/")[-1],
                    url=item.get("url"),
                    downloads=_int_or_none(item.get("downloads")),
                    likes=_int_or_none(item.get("likes")),
                    occurred_at=_parse_dt(item.get("last_modified")),
                    attributes={
                        "tags": (item.get("tags") or [])[:12],
                        "pipeline_tag": item.get("pipeline_tag"),
                    },
                )
            )
    orgs = telemetry.get("organizations") or []
    if orgs:
        out.metrics.append(MetricRow(key="organizations_count", value=float(len(orgs)), unit="count"))


def _mailbox(telemetry: Dict[str, Any], out: NormalizedTelemetry) -> None:
    events = telemetry.get("job_events") or []
    out.job_events = events
    for event in events:
        message_id = event.get("message_id")
        if not message_id:
            continue
        title_bits = [b for b in (event.get("company"), event.get("role")) if b]
        out.artifacts.append(
            ArtifactRow(
                artifact_type="job_email",
                external_id=str(message_id),
                title=" — ".join(title_bits) or event.get("subject"),
                description=event.get("subject"),
                url=event.get("web_link"),
                occurred_at=_parse_dt(event.get("occurred_at")),
                attributes={
                    "category": event.get("category"),
                    "confidence": event.get("confidence"),
                    "company": event.get("company"),
                    "role": event.get("role"),
                    "next_action": event.get("next_action"),
                    "thread_id": event.get("thread_id"),
                },
            )
        )


_ARTIFACT_HANDLERS = {
    "github": _github,
    "leetcode": _leetcode,
    "kaggle": _kaggle,
    "huggingface": _huggingface,
    "google": _mailbox,
    "microsoft": _mailbox,
}
