"""Mock CRM and email draft write tools.

Both write tools are flagged with ``requires_approval=True``. The orchestrator
must pause before invoking their implementation functions.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

try:
    from crewai_tools import tool
except Exception:  # pragma: no cover
    def tool(name: str):
        def decorator(func):
            func.name = name
            func._libra_fallback_tool = True
            return func

        return decorator


def _update_crm_impl(contact_name: str, note: str) -> str:
    try:
        return json.dumps(
            {
                "tool": "update_crm",
                "status": "success",
                "contact_name": contact_name,
                "note": note,
                "crm_record_id": f"crm_{abs(hash(contact_name)) % 100000:05d}",
                "updated_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "mock": True,
            },
            indent=2,
        )
    except Exception as exc:
        return f"ERROR: CRM update failed - {exc}. No record was changed."


def _send_email_draft_impl(to: str, subject: str, body: str) -> str:
    try:
        return json.dumps(
            {
                "tool": "send_email_draft",
                "status": "success",
                "to": to,
                "subject": subject,
                "draft_id": f"draft_{abs(hash(to + subject)) % 100000:05d}",
                "body_preview": body[:240],
                "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "mock": True,
            },
            indent=2,
        )
    except Exception as exc:
        return f"ERROR: Email draft creation failed - {exc}. No draft was created."


@tool("Update CRM")
def update_crm(contact_name: str, note: str) -> str:
    """Update a CRM record with a note after explicit human approval.

    Args:
        contact_name: The contact or account to update.
        note: The CRM note to append.

    Returns:
        A JSON string confirming the mock CRM update.
    """

    # REAL API:
    # Use HubSpot, Salesforce, or another CRM API with OAuth/service credentials.
    # The approval gate must happen before this function is called.
    return _update_crm_impl(contact_name=contact_name, note=note)


@tool("Create Email Draft")
def send_email_draft(to: str, subject: str, body: str) -> str:
    """Create an email draft after explicit human approval.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Full draft body.

    Returns:
        A JSON string confirming the mock email draft.
    """

    # REAL API:
    # Use Gmail API users.drafts.create after OAuth consent and approval.
    # The approval gate must happen before this function is called.
    return _send_email_draft_impl(to=to, subject=subject, body=body)


setattr(update_crm, "requires_approval", True)
setattr(send_email_draft, "requires_approval", True)

__all__ = [
    "update_crm",
    "send_email_draft",
    "_update_crm_impl",
    "_send_email_draft_impl",
]
