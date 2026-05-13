# Module PRD: Safety & Guardrails

## Module Owner
Safety & Guardrails Specialist Agent

## Version
`v1.0`

---

## Objective
Ensure that all write actions (CRM updates, email drafts, Slack messages) require explicit
human approval before execution. This is the most critical trust-building feature for
enterprise use. It must be impossible to bypass.

---

## Scope
This module owns:
- `/libra_app/state/safety.py`
- `/libra_app/components/approval_modal.py`

**Do NOT touch:** Agent logic, tool internals, other state files.

---

## The Golden Rule
```
NO write action EVER executes without explicit user approval.
Not during testing. Not in demo mode. NEVER.
```

---

## Safety Flow

```
Agent calls write tool (e.g., update_crm)
          │
          ▼
Safety layer intercepts call
          │
          ▼
Workflow PAUSES → State: "awaiting_approval"
          │
          ▼
UI shows Approval Modal:
  - Action type (e.g., "Update CRM")
  - Target (e.g., "Contact: John Smith at TechCorp")
  - Proposed change (e.g., "Note: Discussed pricing, interested in Pro plan")
  - [APPROVE] [REJECT] [EDIT] buttons
          │
     ┌────┴────┐
     ▼         ▼
  APPROVE    REJECT
     │         │
     ▼         ▼
  Execute   Cancel → log "User rejected action"
  tool      Workflow continues without write
     │
     ▼
  Log: "Action approved and executed by user"
```

---

## Acceptance Criteria

| # | Criteria |
|---|----------|
| 1 | All tools with `requires_approval=True` pause workflow before executing |
| 2 | Approval modal shows: action type, target, proposed content |
| 3 | User can Approve / Reject / Edit the proposed action |
| 4 | Rejected actions are logged and workflow continues gracefully |
| 5 | Approved actions are executed and confirmed in logs |
| 6 | Safety cannot be bypassed by any agent instruction |
| 7 | LLM system prompt includes explicit safety instructions |

---

## Technical Specifications

### Safety State (safety.py)
```python
class SafetyState(rx.State):
    # Pending approval request
    pending_action: dict = {}
    # e.g., {
    #   "tool": "update_crm",
    #   "params": {"contact_name": "John Smith", "note": "..."},
    #   "agent": "Executor",
    #   "description": "Update CRM record for John Smith at TechCorp",
    #   "timestamp": "2025-01-20T10:30:00"
    # }

    show_approval_modal: bool = False
    approval_result: str = ""  # "approved" | "rejected" | "pending"

    def request_approval(self, tool_name: str, params: dict, description: str):
        """Called by executor when a write tool is about to run."""
        self.pending_action = {
            "tool": tool_name,
            "params": params,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        self.show_approval_modal = True
        self.approval_result = "pending"

    def approve_action(self):
        """User approved the action."""
        self.approval_result = "approved"
        self.show_approval_modal = False
        # Signal to waiting executor thread

    def reject_action(self):
        """User rejected the action."""
        self.approval_result = "rejected"
        self.show_approval_modal = False
        self.pending_action = {}
```

### LLM Safety Prompt (add to all agents)
```python
SAFETY_SYSTEM_PROMPT = """
CRITICAL SAFETY RULES:
1. You MUST NEVER execute write operations (update CRM, send emails, post to Slack)
   without explicit user approval.
2. Before any write action, always call the approval check first.
3. If the user rejects an action, acknowledge it and do not retry the same action.
4. Always clearly describe what you are about to do BEFORE doing it.
5. When in doubt, ask for clarification rather than assuming.
"""
```

### Approval Modal Component (approval_modal.py)
```python
def approval_modal() -> rx.Component:
    return rx.dialog(
        # Shows when SafetyState.show_approval_modal is True
        # Contains:
        # - Action icon + type badge
        # - "The AI wants to perform this action:"
        # - Action description box (styled clearly)
        # - Params preview (target, content)
        # - [Approve] [Reject] buttons
        # - Timestamp
    )
```

---

## Visual Design for Approval Modal
```
┌─────────────────────────────────────────┐
│  ⚠️  Action Requires Your Approval       │
├─────────────────────────────────────────┤
│  ACTION: Update CRM Record              │
│                                         │
│  Target:  John Smith @ TechCorp         │
│  Change:  "Discussed Q1 pricing.        │
│            Interest level: High.        │
│            Follow up next Tuesday."     │
│                                         │
│  Requested by: Executor Agent           │
│  Time: 10:32 AM                        │
├─────────────────────────────────────────┤
│  [✅ Approve]    [✏️ Edit]   [❌ Reject]  │
└─────────────────────────────────────────┘
```

---

## Integration Notes
- Safety state is **called by** Executor agent before any write tool
- Approval modal is **rendered by** `libra_app.py` main layout (always present, hidden by default)
- This module **does not** know about agent internals — it only manages the approval state machine
