"""
libra_app/tools/crm_tool.py
============================
Mock CRM and email draft tools for Libra AI Coworker Demo.
These are WRITE tools — they require human approval before execution.

TODO (v2): Replace mocks with HubSpot/Salesforce API + Gmail drafts API.
"""

import json
from datetime import datetime
from crewai_tools import tool


# ============================================================
# Mock CRM Database — Replace with real API in v2
# ============================================================

MOCK_CRM_RECORDS = {
    "acme corp": {"id": "crm_001", "company": "Acme Corp", "contact": "Sarah Chen", "stage": "Proposal Sent", "notes": []},
    "techcorp": {"id": "crm_002", "company": "TechCorp", "contact": "James Wilson", "stage": "Demo Done", "notes": []},
    "nexus solutions": {"id": "crm_003", "company": "Nexus Solutions", "contact": "Maya Patel", "stage": "Negotiation", "notes": []},
    "startup co": {"id": "crm_004", "company": "StartupCo", "contact": "David Kim", "stage": "Qualified", "notes": []},
}

# Track mock drafts
MOCK_EMAIL_DRAFTS = []


# ============================================================
# Tool Definitions
# ============================================================

@tool("Update CRM Record")
def update_crm(contact_name: str, note: str, stage: str = "") -> str:
    """
    Updates a CRM record with a new note and optionally changes the deal stage.
    IMPORTANT: This is a WRITE operation — always requires explicit user approval before calling.

    Use this after gathering information about a contact to log what was learned or decided.

    Args:
        contact_name: Name of the contact or company (e.g., "Sarah Chen" or "Acme Corp")
        note: The note to add to the CRM record (be specific and professional)
        stage: Optional new deal stage (e.g., "Proposal Sent", "Negotiation", "Closed Won")

    Returns:
        JSON string confirming the CRM update with record ID and timestamp
    """
    # ================================================================
    # REAL API IMPLEMENTATION (v2 TODO — HubSpot):
    # ================================================================
    # import hubspot
    # from hubspot.crm.contacts import SimplePublicObjectInput
    #
    # client = hubspot.Client.create(access_token=os.environ["HUBSPOT_ACCESS_TOKEN"])
    #
    # # Find contact by name
    # search = client.crm.contacts.search_api.do_search(...)
    # contact_id = search.results[0].id
    #
    # # Add note as engagement
    # client.crm.objects.notes.basic_api.create(
    #     simple_public_object_input_for_create={
    #         "properties": {
    #             "hs_note_body": note,
    #             "hs_timestamp": datetime.now().isoformat()
    #         },
    #         "associations": [{"to": {"id": contact_id}, "types": [{"category": "HUBSPOT_DEFINED", "typeId": 202}]}]
    #     }
    # )
    # ================================================================

    # MOCK IMPLEMENTATION
    contact_key = contact_name.lower()

    # Find matching record (fuzzy match)
    matched_record = None
    for key, record in MOCK_CRM_RECORDS.items():
        if key in contact_key or contact_key in key:
            matched_record = record
            break

    # Create a new record if not found
    if not matched_record:
        matched_record = {
            "id": f"crm_{len(MOCK_CRM_RECORDS) + 1:03d}",
            "company": contact_name,
            "contact": contact_name,
            "stage": stage or "New",
            "notes": [],
        }

    # Add the note
    new_note = {
        "text": note,
        "timestamp": datetime.now().isoformat(),
        "author": "Libra AI (Auto)",
    }
    matched_record["notes"].append(new_note)

    # Update stage if provided
    if stage:
        matched_record["stage"] = stage

    result = {
        "success": True,
        "action": "CRM record updated",
        "record_id": matched_record["id"],
        "contact": matched_record["contact"],
        "company": matched_record["company"],
        "new_note": note,
        "stage": matched_record["stage"],
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": "[MOCK — Real CRM API not connected in v1]"
    }

    return json.dumps(result, indent=2)


@tool("Create Email Draft")
def send_email_draft(to: str, subject: str, body: str) -> str:
    """
    Creates an email draft in Gmail for the user to review and send.
    IMPORTANT: This is a WRITE operation — always requires explicit user approval before calling.

    Use this to prepare professional emails based on research and analysis.
    The draft is NOT sent automatically — the user must review and send it manually.

    Args:
        to: Recipient email address (e.g., "sarah@acmecorp.com")
        subject: Email subject line
        body: Full email body (professional tone, plain text or markdown)

    Returns:
        JSON string with draft ID and preview confirming it was created
    """
    # ================================================================
    # REAL API IMPLEMENTATION (v2 TODO — Gmail API):
    # ================================================================
    # from googleapiclient.discovery import build
    # from email.mime.text import MIMEText
    # import base64
    #
    # service = build('gmail', 'v1', credentials=get_creds())
    #
    # message = MIMEText(body)
    # message['to'] = to
    # message['subject'] = subject
    # raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    #
    # draft = service.users().drafts().create(
    #     userId='me',
    #     body={'message': {'raw': raw}}
    # ).execute()
    # return json.dumps({"draft_id": draft['id'], "status": "created"})
    # ================================================================

    # MOCK IMPLEMENTATION
    draft_id = f"draft_{len(MOCK_EMAIL_DRAFTS) + 1:03d}_{datetime.now().strftime('%H%M%S')}"

    draft = {
        "id": draft_id,
        "to": to,
        "subject": subject,
        "body_preview": body[:200] + ("..." if len(body) > 200 else ""),
        "body_length": len(body),
        "status": "draft_created",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    MOCK_EMAIL_DRAFTS.append(draft)

    result = {
        "success": True,
        "action": "Email draft created",
        "draft_id": draft_id,
        "to": to,
        "subject": subject,
        "body_preview": draft["body_preview"],
        "next_step": "Draft saved. Please review in Gmail before sending.",
        "note": "[MOCK — Real Gmail API not connected in v1]"
    }

    return json.dumps(result, indent=2)
