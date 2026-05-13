"""
tests/test_tools.py
====================
Unit tests for mock tool integrations.
Run with: pytest tests/test_tools.py -v
"""

import json
import pytest
from libra_app.tools.gmail_tool import search_gmail
from libra_app.tools.slack_tool import search_slack
from libra_app.tools.crm_tool import update_crm, send_email_draft


class TestGmailTool:
    def test_returns_json_string(self):
        result = search_gmail.run("test query")
        data = json.loads(result)
        assert "emails" in data
        assert isinstance(data["emails"], list)

    def test_keyword_filtering(self):
        result = search_gmail.run("Acme Corp")
        data = json.loads(result)
        assert data["total_found"] > 0

    def test_default_days(self):
        result = search_gmail.run("leads")
        data = json.loads(result)
        assert data["days_searched"] == 7

    def test_empty_query_returns_results(self):
        result = search_gmail.run("")
        data = json.loads(result)
        assert len(data["emails"]) > 0


class TestSlackTool:
    def test_returns_json_string(self):
        result = search_slack.run("#sales")
        data = json.loads(result)
        assert "messages" in data

    def test_channel_with_hash(self):
        result = search_slack.run("#sales")
        data = json.loads(result)
        assert data["channel"] == "#sales"

    def test_channel_without_hash(self):
        result = search_slack.run("sales")
        data = json.loads(result)
        assert data["channel"] == "#sales"

    def test_unknown_channel_returns_default(self):
        result = search_slack.run("#nonexistent")
        data = json.loads(result)
        assert len(data["messages"]) > 0


class TestCRMTool:
    def test_update_known_contact(self):
        result = update_crm.run("Acme Corp", "Discussed Q1 pricing")
        data = json.loads(result)
        assert data["success"] is True
        assert "Acme" in data["company"]

    def test_update_unknown_contact_creates_record(self):
        result = update_crm.run("BrandNewCorp", "Initial contact made")
        data = json.loads(result)
        assert data["success"] is True

    def test_note_is_saved(self):
        note = "This is a specific test note"
        result = update_crm.run("TechCorp", note)
        data = json.loads(result)
        assert data["new_note"] == note


class TestEmailDraftTool:
    def test_creates_draft(self):
        result = send_email_draft.run(
            "test@example.com",
            "Test Subject",
            "Test email body"
        )
        data = json.loads(result)
        assert data["success"] is True
        assert "draft_id" in data

    def test_draft_id_is_unique(self):
        r1 = json.loads(send_email_draft.run("a@b.com", "Sub1", "Body1"))
        r2 = json.loads(send_email_draft.run("a@b.com", "Sub2", "Body2"))
        assert r1["draft_id"] != r2["draft_id"]
