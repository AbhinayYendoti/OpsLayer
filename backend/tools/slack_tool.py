"""Mock Slack integration for Libra AI Coworker."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

try:
    from crewai_tools import tool
except Exception:  # pragma: no cover
    def tool(name: str):
        def decorator(func):
            func.name = name
            func._libra_fallback_tool = True
            return func

        return decorator


def _timestamp(hours_ago: int) -> str:
    return (datetime.now(UTC) - timedelta(hours=hours_ago)).isoformat(timespec="seconds")


MOCK_MESSAGES: list[dict[str, Any]] = [
    {
        "id": "slk_001",
        "channel": "#sales",
        "author": "Priya Shah",
        "timestamp": _timestamp(2),
        "text": "Acme Corp asked for a security addendum and wants the pilot kickoff on Tuesday.",
        "reactions": ["eyes", "white_check_mark"],
    },
    {
        "id": "slk_002",
        "channel": "#sales",
        "author": "Marcus Lee",
        "timestamp": _timestamp(4),
        "text": "TechCorp is still active. James said workflow audit logs are the biggest differentiator.",
        "reactions": ["chart_with_upwards_trend"],
    },
    {
        "id": "slk_003",
        "channel": "#customer-success",
        "author": "Elena Rodriguez",
        "timestamp": _timestamp(7),
        "text": "Nexus Solutions renewal is likely to expand if we can answer procurement by Thursday.",
        "reactions": ["memo"],
    },
    {
        "id": "slk_004",
        "channel": "#sales",
        "author": "Noah Bennett",
        "timestamp": _timestamp(8),
        "text": "StartupCo requested enterprise SSO docs and an implementation plan for next month.",
        "reactions": [],
    },
    {
        "id": "slk_005",
        "channel": "#sales",
        "author": "Priya Shah",
        "timestamp": _timestamp(11),
        "text": "Daily sales digest: 3 active late-stage accounts, 2 procurement blockers, 1 new pilot.",
        "reactions": ["pushpin"],
    },
]


def _search_slack_impl(channel: str = "#sales", query: str = "") -> str:
    try:
        normalized_channel = channel if channel.startswith("#") else f"#{channel}"
        words = [word for word in query.lower().replace("#", " ").split() if len(word) > 2]
        matches = []
        for message in MOCK_MESSAGES:
            same_channel = message["channel"].lower() == normalized_channel.lower()
            haystack = " ".join(str(value).lower() for value in message.values())
            query_match = not words or any(word in haystack for word in words)
            if same_channel and query_match:
                matches.append(message)

        if not matches:
            matches = [msg for msg in MOCK_MESSAGES if msg["channel"].lower() == normalized_channel.lower()]
        if not matches:
            matches = MOCK_MESSAGES[:3]

        return json.dumps(
            {
                "source": "slack",
                "channel": normalized_channel,
                "query": query,
                "total_found": len(matches),
                "messages": matches,
                "mock": True,
            },
            indent=2,
        )
    except Exception as exc:
        return f"ERROR: Slack search failed - {exc}. Please check the channel and query."


@tool("Search Slack")
def search_slack(channel: str = "#sales", query: str = "") -> str:
    """Search Slack messages in a channel for a query.

    Args:
        channel: Slack channel name, with or without leading #.
        query: Search terms such as a company, topic, or person.

    Returns:
        A JSON string containing matching Slack messages.
    """

    # REAL API:
    # Use Slack Web API conversations.history and search.messages with a bot
    # token, then normalize timestamps, authors, thread context, and reactions.
    return _search_slack_impl(channel=channel, query=query)


setattr(search_slack, "requires_approval", False)

__all__ = ["search_slack", "_search_slack_impl"]
