# Module PRD: Tool Integrations

## Module Owner
Tool Integrations Specialist Agent

## Version
`v1.0`

---

## Objective
Build clean, consistent, and easily replaceable mock tools for Gmail, Slack, and CRM.
Each tool must be production-quality Python with clear comments showing where real API
calls would replace the mock logic.

---

## Scope
This module owns:
- `/libra_app/tools/gmail_tool.py`
- `/libra_app/tools/slack_tool.py`
- `/libra_app/tools/crm_tool.py`

**Do NOT touch:** Agent definitions, UI components, state management, safety layer.

---

## Tools Required

### Tool 1: search_gmail
| Property | Value |
|----------|-------|
| Function | `search_gmail(query: str, days: int = 7) -> str` |
| Mock Data | Returns 2-3 realistic fake emails |
| Requires Approval | ❌ No (read-only) |
| Future Real API | Gmail API v1 with OAuth2 |

### Tool 2: search_slack
| Property | Value |
|----------|-------|
| Function | `search_slack(channel: str, query: str) -> str` |
| Mock Data | Returns 3-5 realistic fake Slack messages |
| Requires Approval | ❌ No (read-only) |
| Future Real API | Slack Web API with Bot Token |

### Tool 3: update_crm
| Property | Value |
|----------|-------|
| Function | `update_crm(contact_name: str, note: str) -> str` |
| Mock Data | Confirms fake CRM update |
| Requires Approval | ✅ YES — must pause and request user confirmation |
| Future Real API | Salesforce / HubSpot API |

### Tool 4: send_email_draft
| Property | Value |
|----------|-------|
| Function | `send_email_draft(to: str, subject: str, body: str) -> str` |
| Mock Data | Returns draft ID |
| Requires Approval | ✅ YES — must pause and request user confirmation |
| Future Real API | Gmail API drafts.create |

---

## Acceptance Criteria

| # | Criteria |
|---|----------|
| 1 | All tools use CrewAI `@tool` decorator |
| 2 | All tools return a **string** (CrewAI requirement) |
| 3 | Mock responses are realistic (names, dates, plausible content) |
| 4 | Every tool has a `# REAL API:` comment block |
| 5 | Write tools (`update_crm`, `send_email_draft`) are flagged with `requires_approval=True` |
| 6 | All tools handle and return errors gracefully (no crashes) |
| 7 | Tool docstrings are complete (used by LLM for tool selection) |

---

## Technical Specifications

### Tool Pattern (REQUIRED for all tools)
```python
from crewai_tools import tool
import json
from datetime import datetime

@tool("Search Gmail")
def search_gmail(query: str, days: int = 7) -> str:
    """
    Searches Gmail inbox for emails matching the query within the last N days.
    Returns a formatted list of matching emails with subject, sender, and summary.

    Args:
        query: Search keywords (e.g., "Acme Corp proposal")
        days: How many days back to search (default: 7)

    Returns:
        Formatted string with email results
    """
    # ================================================================
    # REAL API IMPLEMENTATION (Future):
    # from googleapiclient.discovery import build
    # service = build('gmail', 'v1', credentials=creds)
    # results = service.users().messages().list(userId='me', q=query).execute()
    # ================================================================

    # MOCK IMPLEMENTATION
    mock_emails = [
        {
            "id": "msg_001",
            "from": "sarah@acmecorp.com",
            "subject": f"Re: Proposal for {query}",
            "date": "2025-01-20",
            "snippet": "Thanks for sending over the proposal. We've reviewed it and..."
        },
        ...
    ]
    return json.dumps(mock_emails, indent=2)
```

### Mock Data Quality Standards
- Use realistic company names: Acme Corp, TechCorp, Nexus Solutions
- Use realistic names: Sarah Chen, James Wilson, Maya Patel
- Dates should be within last 7-30 days of current date
- Email/Slack content should be relevant to a B2B SaaS context

### Error Handling Pattern
```python
try:
    # tool logic
    return result
except Exception as e:
    return f"ERROR: Tool failed — {str(e)}. Please try again or check inputs."
```

---

## File Structure
```python
# gmail_tool.py
from crewai_tools import tool

REQUIRES_APPROVAL = False  # Set True for write tools

@tool("Search Gmail")
def search_gmail(...) -> str:
    ...

# Export for use in agents
__all__ = ["search_gmail"]
```

---

## Integration Notes
- Tools are **imported by** agent files in `/libra_app/agents/`
- `requires_approval=True` tools trigger the Safety module flow
- All tool outputs are **strings** — format JSON as strings if needed
- Tool names in `@tool("Name")` must be clear — LLM uses them for routing
