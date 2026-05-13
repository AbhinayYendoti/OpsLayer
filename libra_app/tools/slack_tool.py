"""
libra_app/tools/slack_tool.py
==============================
Mock Slack tool for Libra AI Coworker Demo.
Simulates searching Slack channels with realistic fake data.

TODO (v2): Replace mock with real Slack Web API integration.
"""

import json
from datetime import datetime, timedelta
from crewai_tools import tool


# ============================================================
# Mock Data — Replace with real Slack API in v2
# ============================================================

MOCK_SLACK_MESSAGES = {
    "#sales": [
        {
            "id": "msg_s001",
            "user": "alex.morgan",
            "text": "Just closed TechCorp! 45-seat Enterprise deal. 🎉 Q1 is looking great.",
            "timestamp": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
            "reactions": ["🎉", "🔥", "💪"],
        },
        {
            "id": "msg_s002",
            "user": "priya.sharma",
            "text": "Heads up: Nexus Solutions is evaluating a competitor. Demo went well but they want a pricing concession. Looping in Sarah for approval.",
            "timestamp": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
            "reactions": ["👀"],
        },
        {
            "id": "msg_s003",
            "user": "tom.bradley",
            "text": "Pipeline update: 12 new leads from the webinar yesterday. Assigning 4 to each AE. HubSpot is updated.",
            "timestamp": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            "reactions": ["👍"],
        },
        {
            "id": "msg_s004",
            "user": "sarah.chen",
            "text": "@priya.sharma approved 10% discount for Nexus if they sign before end of quarter. Go for it!",
            "timestamp": (datetime.now() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
            "reactions": [],
        },
        {
            "id": "msg_s005",
            "user": "alex.morgan",
            "text": "Reminder: Friday all-hands sales review at 3pm. Please update your deals in HubSpot by Thursday EOD.",
            "timestamp": (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"),
            "reactions": ["✅", "✅", "✅"],
        },
    ],
    "#general": [
        {
            "id": "msg_g001",
            "user": "ceo.mike",
            "text": "Team: we just hit our Q4 revenue target! 🚀 Huge thanks to everyone. Pizza lunch on Friday to celebrate.",
            "timestamp": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
            "reactions": ["🎉", "🍕", "❤️"],
        },
        {
            "id": "msg_g002",
            "user": "hr.team",
            "text": "Reminder: Open enrollment for benefits closes this Friday. Please log into BambooHR to review your selections.",
            "timestamp": (datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M"),
            "reactions": ["✅"],
        },
    ],
    "#engineering": [
        {
            "id": "msg_e001",
            "user": "dev.team",
            "text": "Deployed v2.4.1 to production. Includes the new agent memory fixes and performance improvements. Monitoring looks clean. 🟢",
            "timestamp": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            "reactions": ["🚀", "✅"],
        },
        {
            "id": "msg_e002",
            "user": "backend.lead",
            "text": "Found a memory leak in the context manager. Fix is in PR #247. Review needed before Monday release.",
            "timestamp": (datetime.now() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"),
            "reactions": ["👀"],
        },
    ],
}


# ============================================================
# Tool Definition
# ============================================================

@tool("Search Slack")
def search_slack(channel: str = "#sales", query: str = "", limit: int = 5) -> str:
    """
    Searches a Slack channel for recent messages matching the query.
    Returns the most recent relevant messages with sender, text, and timestamp.

    Use this to find conversations, decisions, updates, or action items in Slack channels.

    Args:
        channel: Slack channel name with # prefix (e.g., "#sales", "#general", "#engineering")
        query: Search keywords (optional — if empty, returns recent messages)
        limit: Maximum number of messages to return (default: 5)

    Returns:
        JSON string containing channel messages with user, text, timestamp, and reactions
    """
    # ================================================================
    # REAL API IMPLEMENTATION (v2 TODO):
    # ================================================================
    # from slack_sdk import WebClient
    #
    # client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    #
    # response = client.conversations_history(
    #     channel=get_channel_id(channel),  # Need to resolve name → ID
    #     limit=limit
    # )
    # messages = response["messages"]
    #
    # If query provided, also use search:
    # search_response = client.search_messages(query=f"in:{channel} {query}")
    # ================================================================

    # MOCK IMPLEMENTATION
    # Normalize channel name
    channel_key = channel if channel.startswith("#") else f"#{channel}"
    channel_messages = MOCK_SLACK_MESSAGES.get(channel_key, MOCK_SLACK_MESSAGES["#sales"])

    # Filter by query if provided
    if query:
        query_lower = query.lower()
        filtered = [
            msg for msg in channel_messages
            if any(word in msg["text"].lower() for word in query_lower.split())
        ]
        # Fall back to all messages if no match
        matching = filtered if filtered else channel_messages
    else:
        matching = channel_messages

    # Apply limit
    matching = matching[:limit]

    result = {
        "channel": channel_key,
        "query": query or "(all recent)",
        "message_count": len(matching),
        "messages": matching,
        "note": "[MOCK DATA — Real Slack API not connected in v1]"
    }

    return json.dumps(result, indent=2)
