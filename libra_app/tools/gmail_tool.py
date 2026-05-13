"""
libra_app/tools/gmail_tool.py
==============================
Mock Gmail tool for Libra AI Coworker Demo.
Simulates searching Gmail inbox with realistic fake data.

TODO (v2): Replace mock with real Gmail API v1 integration.
"""

import json
from datetime import datetime, timedelta
from crewai_tools import tool


# ============================================================
# Mock Data — Replace with real API in v2
# ============================================================

MOCK_EMAILS = [
    {
        "id": "msg_001",
        "from": "sarah.chen@acmecorp.com",
        "subject": "Re: Q1 Partnership Proposal",
        "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "snippet": "Thanks for the detailed proposal. We've reviewed it internally and the team is quite interested. Can we schedule a call this week to discuss pricing?",
        "labels": ["INBOX", "IMPORTANT"],
    },
    {
        "id": "msg_002",
        "from": "james.wilson@techcorp.io",
        "subject": "Follow-up: Product Demo",
        "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
        "snippet": "Hi! Just following up on last week's demo. Our CTO was impressed with the automation features. We're comparing you against one other vendor — decision by Friday.",
        "labels": ["INBOX"],
    },
    {
        "id": "msg_003",
        "from": "maya.patel@nexussolutions.com",
        "subject": "Contract renewal discussion",
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "snippet": "Our current contract expires in 30 days. Happy with the service but need to discuss volume pricing before renewal. Are you free this week?",
        "labels": ["INBOX", "STARRED"],
    },
    {
        "id": "msg_004",
        "from": "david.kim@startupco.com",
        "subject": "Interested in Enterprise plan",
        "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "snippet": "We've outgrown our current plan. Team is now 45 people. Would love to understand what the Enterprise tier includes and what the upgrade path looks like.",
        "labels": ["INBOX"],
    },
    {
        "id": "msg_005",
        "from": "lisa.torres@globalventures.com",
        "subject": "Meeting recap + next steps",
        "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "snippet": "Great meeting yesterday! As discussed: we'll run a 2-week pilot starting Monday. I'll have our IT team reach out to set up SSO. LMK if you need anything from our side.",
        "labels": ["INBOX", "IMPORTANT"],
    },
]


# ============================================================
# Tool Definition
# ============================================================

@tool("Search Gmail")
def search_gmail(query: str, days: int = 7) -> str:
    """
    Searches Gmail inbox for emails matching the query within the last N days.
    Returns a formatted list of relevant emails with subject, sender, date, and preview.

    Use this to find emails from specific people, about specific topics, or within a date range.

    Args:
        query: Search keywords (e.g., "Acme Corp proposal", "leads", "follow-up")
        days: How many days back to search (default: 7, max: 30)

    Returns:
        JSON string containing list of matching emails with id, from, subject, date, snippet
    """
    # ================================================================
    # REAL API IMPLEMENTATION (v2 TODO):
    # ================================================================
    # from googleapiclient.discovery import build
    # from google.oauth2.credentials import Credentials
    #
    # creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # service = build('gmail', 'v1', credentials=creds)
    #
    # results = service.users().messages().list(
    #     userId='me',
    #     q=f"{query} newer_than:{days}d",
    #     maxResults=10
    # ).execute()
    #
    # messages = results.get('messages', [])
    # emails = []
    # for msg in messages:
    #     detail = service.users().messages().get(userId='me', id=msg['id']).execute()
    #     emails.append(parse_email(detail))
    # return json.dumps(emails)
    # ================================================================

    # MOCK IMPLEMENTATION
    # Simple keyword filter on mock data
    query_lower = query.lower()
    matching = []

    for email in MOCK_EMAILS:
        text_to_search = (
            email["subject"].lower() + " " +
            email["snippet"].lower() + " " +
            email["from"].lower()
        )
        # Match if any query word appears in email content
        if any(word in text_to_search for word in query_lower.split()):
            matching.append(email)

    # If no keyword match, return first 3 as general inbox results
    if not matching:
        matching = MOCK_EMAILS[:3]

    result = {
        "query": query,
        "days_searched": days,
        "total_found": len(matching),
        "emails": matching,
        "note": "[MOCK DATA — Real Gmail API not connected in v1]"
    }

    return json.dumps(result, indent=2)
