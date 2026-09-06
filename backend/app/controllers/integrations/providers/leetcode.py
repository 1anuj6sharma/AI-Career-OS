"""
LeetCode connector — public profile, no OAuth.

LeetCode publishes no OAuth programme and no documented REST API.  It does
expose the same public GraphQL endpoint its own website uses
(`https://leetcode.com/graphql/`), which serves only data a user has already
made public on their profile page.  We use that endpoint read-only and we never
ask for LeetCode credentials.

Because the endpoint is undocumented and unversioned it can change without
notice; the connector is therefore declared LIMITED and every field is reported
as `null` rather than `0` when LeetCode does not return it (spec §10, §25).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from . import http
from .base import (
    AuthMethod,
    Capability,
    ProviderDescriptor,
    ProviderError,
    PublicProfileProvider,
    sanitize_username,
)

GRAPHQL = "https://leetcode.com/graphql/"

PROFILE_QUERY = """
query aiCareerOsProfile($username: String!) {
  matchedUser(username: $username) {
    username
    githubUrl
    twitterUrl
    linkedinUrl
    profile {
      realName
      userAvatar
      aboutMe
      countryName
      company
      school
      ranking
      reputation
      skillTags
    }
  }
}
"""

STATS_QUERY = """
query aiCareerOsStats($username: String!) {
  matchedUser(username: $username) {
    username
    profile { ranking reputation }
    submitStatsGlobal { acSubmissionNum { difficulty count submissions } }
    languageProblemCount { languageName problemsSolved }
    tagProblemCounts {
      advanced { tagName problemsSolved }
      intermediate { tagName problemsSolved }
      fundamental { tagName problemsSolved }
    }
  }
  userContestRanking(username: $username) {
    rating
    attendedContestsCount
    globalRanking
    totalParticipants
    topPercentage
  }
  recentAcSubmissionList(username: $username, limit: 15) {
    title
    titleSlug
    timestamp
  }
}
"""

DESCRIPTOR = ProviderDescriptor(
    name="leetcode",
    display_name="LeetCode",
    auth_method=AuthMethod.PUBLIC_USERNAME,
    capabilities=frozenset(
        {Capability.IDENTITY, Capability.PROFILE, Capability.STATS, Capability.ACTIVITY}
    ),
    limitation_note=(
        "LeetCode offers no official OAuth or public API. We read only the public "
        "data on your profile using the same endpoint leetcode.com itself uses. "
        "Your profile must be public, and LeetCode may change this endpoint at any time."
    ),
    docs_url="https://leetcode.com/",
    profile_url_template="https://leetcode.com/u/{username}/",
    allowed_url_hosts=("leetcode.com",),
)


async def _graphql(query: str, username: str, *, action: str) -> Dict[str, Any]:
    payload = await http.request_json(
        "LeetCode",
        "POST",
        GRAPHQL,
        action=action,
        headers={
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/u/{username}/",
            "Origin": "https://leetcode.com",
        },
        json={"query": query, "variables": {"username": username}},
    )
    if not isinstance(payload, dict):
        raise ProviderError(
            "LeetCode returned an unexpected response.",
            detail=f"LeetCode {action}: non-object payload",
            code="invalid_response",
        )
    if payload.get("errors"):
        first = (payload["errors"] or [{}])[0]
        message = str(first.get("message", ""))
        if "does not exist" in message.lower() or "not found" in message.lower():
            raise ProviderError(
                f"No public LeetCode profile found for '{username}'.",
                detail=f"LeetCode {action}: {message}",
                code="account_not_found",
            )
        raise ProviderError(
            "LeetCode could not return that profile.",
            detail=f"LeetCode {action}: {message}",
            code="provider_error",
        )
    return payload.get("data") or {}


class LeetCodeProvider(PublicProfileProvider):
    @property
    def descriptor(self) -> ProviderDescriptor:
        return DESCRIPTOR

    async def validate_and_get_profile(self, identifier: str) -> Dict[str, Any]:
        username = sanitize_username(identifier)
        data = await _graphql(PROFILE_QUERY, username, action="fetch profile")
        matched = data.get("matchedUser")
        if not matched:
            raise ProviderError(
                f"No public LeetCode profile found for '{username}'. Check the username and that your profile is public.",
                detail=f"LeetCode matchedUser was null for {username}",
                code="account_not_found",
            )
        profile = matched.get("profile") or {}
        real_username = matched.get("username") or username
        return {
            "provider_account_id": real_username,
            "provider_username": real_username,
            "display_name": profile.get("realName") or real_username,
            "email": None,
            "profile_url": f"https://leetcode.com/u/{real_username}/",
            "avatar_url": profile.get("userAvatar"),
        }

    async def get_telemetry(self, identifier: str) -> Dict[str, Any]:
        username = sanitize_username(identifier)
        data = await _graphql(STATS_QUERY, username, action="fetch stats")
        matched = data.get("matchedUser")
        if not matched:
            raise ProviderError(
                f"No public LeetCode profile found for '{username}'.",
                detail=f"LeetCode matchedUser was null for {username}",
                code="account_not_found",
            )

        solved: Dict[str, Optional[int]] = {"total": None, "easy": None, "medium": None, "hard": None}
        submissions_total: Optional[int] = None
        stats = (matched.get("submitStatsGlobal") or {}).get("acSubmissionNum") or []
        for bucket in stats:
            difficulty = str(bucket.get("difficulty", "")).lower()
            count = bucket.get("count")
            if difficulty == "all":
                solved["total"] = count
                submissions_total = bucket.get("submissions")
            elif difficulty in solved:
                solved[difficulty] = count

        contest = data.get("userContestRanking") or {}
        rating = contest.get("rating")
        top_percentage = contest.get("topPercentage")

        languages: List[Dict[str, Any]] = [
            {"language": item.get("languageName"), "solved": item.get("problemsSolved")}
            for item in (matched.get("languageProblemCount") or [])
            if item.get("languageName")
        ]
        languages.sort(key=lambda x: x.get("solved") or 0, reverse=True)

        tags = matched.get("tagProblemCounts") or {}
        topic_strengths = {
            level: [
                {"topic": t.get("tagName"), "solved": t.get("problemsSolved")}
                for t in (tags.get(level) or [])
                if (t.get("problemsSolved") or 0) > 0
            ][:10]
            for level in ("advanced", "intermediate", "fundamental")
        }

        profile = matched.get("profile") or {}
        return {
            "username": matched.get("username") or username,
            "solved_total": solved["total"],
            "solved_easy": solved["easy"],
            "solved_medium": solved["medium"],
            "solved_hard": solved["hard"],
            "total_accepted_submissions": submissions_total,
            "global_ranking": profile.get("ranking"),
            "reputation": profile.get("reputation"),
            "contest_rating": round(rating, 2) if isinstance(rating, (int, float)) else None,
            "contests_attended": contest.get("attendedContestsCount"),
            "contest_global_ranking": contest.get("globalRanking"),
            "contest_total_participants": contest.get("totalParticipants"),
            "contest_top_percentage": (
                round(top_percentage, 2) if isinstance(top_percentage, (int, float)) else None
            ),
            "has_contest_history": bool(contest),
            "languages": languages[:10],
            "topic_strengths": topic_strengths,
            "recent_solved": [
                {"title": s.get("title"), "slug": s.get("titleSlug"), "timestamp": s.get("timestamp")}
                for s in (data.get("recentAcSubmissionList") or [])
            ],
            "data_source": "leetcode.com public GraphQL endpoint (unofficial, undocumented)",
        }

    async def health_check(self) -> Dict[str, Any]:
        result = await http.probe("https://leetcode.com/", expected=(200, 403))
        return {
            "provider": self.provider_name,
            "configured": True,
            "limitation_note": DESCRIPTOR.limitation_note,
            **result,
        }
