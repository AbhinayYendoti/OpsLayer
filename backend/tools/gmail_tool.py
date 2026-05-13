"""Mock Gmail integration for Libra AI Coworker.

The tool returns realistic B2B email data as a JSON string so CrewAI can consume
it directly. Replace the mock block with Gmail API calls when OAuth is added.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

try:
    from crewai_tools import tool
except Exception:  # pragma: no cover - lets the API boot before deps install.
    def tool(name: str):
        def decorator(func):
            func.name = name
            func._libra_fallback_tool = True
            return func

        return decorator


def _email_date(days_ago: int) -> str:
    return (datetime.now(UTC) - timedelta(days=days_ago)).date().isoformat()


MOCK_EMAILS: list[dict[str, Any]] = [
    {
        "id": "msg_20260511_001",
        "from": "Sarah Chen <sarah.chen@acmecorp.com>",
        "company": "Acme Corp",
        "subject": "Re: Q2 automation rollout and pricing",
        "date": _email_date(2),
        "snippet": (
            "The operations team approved the pilot scope. We need a CRM note "
            "capturing security review status, budget owner, and next Tuesday's call."
        ),
        "labels": ["INBOX", "IMPORTANT"],
    },
    {
        "id": "msg_20260509_014",
        "from": "James Wilson <james.wilson@techcorp.io>",
        "company": "TechCorp",
        "subject": "Product demo follow-up",
        "date": _email_date(4),
        "snippet": (
            "Our CTO liked the workflow visibility and approval controls. We are "
            "comparing two vendors and expect a decision by Friday."
        ),
        "labels": ["INBOX"],
    },
    {
        "id": "msg_20260512_023",
        "from": "Maya Patel <maya.patel@nexussolutions.com>",
        "company": "Nexus Solutions",
        "subject": "Renewal discussion and usage expansion",
        "date": _email_date(1),
        "snippet": (
            "The account is ready to expand from 35 to 120 seats if procurement "
            "can confirm volume pricing this week."
        ),
        "labels": ["INBOX", "STARRED"],
    },
    {
        "id": "msg_20260506_037",
        "from": "David Kim <david.kim@startupco.com>",
        "company": "StartupCo",
        "subject": "Enterprise plan evaluation",
        "date": _email_date(7),
        "snippet": (
            "We have outgrown the team plan. Please send enterprise details, SSO "
            "requirements, and onboarding timelines for a 50-person team."
        ),
        "labels": ["INBOX"],
    },
]


def _matches_query(email: dict[str, Any], query: str) -> bool:
    words = [word for word in query.lower().replace("#", " ").split() if len(word) > 2]
    haystack = " ".join(str(value).lower() for value in email.values())
    return not words or any(word in haystack for word in words)


def _search_gmail_impl(query: str, days: int = 7) -> str:
    try:
        days = max(1, min(int(days), 30))
        cutoff = datetime.now(UTC).date() - timedelta(days=days)
        matches = [
            email
            for email in MOCK_EMAILS
            if datetime.fromisoformat(email["date"]).date() >= cutoff
            and _matches_query(email, query)
        ]
        if not matches:
            matches = MOCK_EMAILS[:3]

        return json.dumps(
            {
                "source": "gmail",
                "query": query,
                "days_searched": days,
                "total_found": len(matches),
                "emails": matches,
                "mock": True,
            },
            indent=2,
        )
    except Exception as exc:
        return f"ERROR: Gmail search failed - {exc}. Please refine the query."


@tool("Search Gmail")
def search_gmail(query: str, days: int = 7) -> str:
    """Search Gmail for messages matching a query within the last N days.

    Args:
        query: Search terms such as a company, person, or topic.
        days: Number of days to search back, from 1 to 30.

    Returns:
        A JSON string containing matching emails.
    """

    # REAL API:
    # Use Gmail API v1 with OAuth2 credentials, query messages using the Gmail
    # search syntax, then fetch and normalize message headers/snippets.
    return _search_gmail_impl(query=query, days=days)


setattr(search_gmail, "requires_approval", False)

__all__ = ["search_gmail", "_search_gmail_impl"]
