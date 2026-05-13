# Module PRD: Memory & Context

## Module Owner
Memory & Context Specialist Agent

## Version
`v1.0`

---

## Objective
Maintain reliable context across all agents during a single workflow execution.
Ensure that information found by the Researcher is available to the Analyst and Executor
without repetition or loss. Keep session state clean for the UI.

---

## Scope
This module owns:
- `/libra_app/state/memory.py`
- `/libra_app/state/app_state.py`

**Do NOT touch:** Agent logic, tool internals, UI components, safety layer.

---

## Memory Types (v1)

| Type | Scope | Storage | Notes |
|------|-------|---------|-------|
| Workflow Memory | Within one crew run | CrewAI built-in memory | Automatic |
| Session State | Current UI session | Reflex State | In-memory |
| Step Log | Current workflow | Reflex State list | Shown in UI |
| Long-term Memory | ❌ Not in v1 | — | Future: SQLite |

---

## Acceptance Criteria

| # | Criteria |
|---|----------|
| 1 | Tool results from Researcher are accessible to Analyst in same crew run |
| 2 | Workflow step log persists for the full session (not cleared on each run) |
| 3 | Context is efficiently summarized when approaching LLM token limits |
| 4 | Session history (past workflows) is stored and accessible in sidebar |
| 5 | State resets cleanly when user starts a new workflow |

---

## Technical Specifications

### App State (app_state.py)
```python
import reflex as rx
from typing import List, Dict, Any
from datetime import datetime

class WorkflowStep(rx.Base):
    step_number: int
    agent: str           # "Researcher" | "Analyst" | "Executor" | "Manager"
    action: str          # Description of what happened
    result: str          # Output / result
    status: str          # "running" | "done" | "error" | "waiting_approval"
    timestamp: str

class WorkflowRun(rx.Base):
    id: str
    input: str           # Original user request
    steps: List[WorkflowStep]
    final_result: str
    status: str          # "running" | "complete" | "failed"
    created_at: str

class AppState(rx.State):
    # Current workflow
    current_input: str = ""
    current_steps: List[WorkflowStep] = []
    current_status: str = "idle"  # idle | running | complete | error

    # Session history
    workflow_history: List[WorkflowRun] = []

    # UI state
    is_loading: bool = False
    error_message: str = ""

    def add_step(self, agent: str, action: str, result: str = "", status: str = "running"):
        """Add a new step to the current workflow log."""
        step = WorkflowStep(
            step_number=len(self.current_steps) + 1,
            agent=agent,
            action=action,
            result=result,
            status=status,
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        self.current_steps.append(step)

    def update_last_step(self, result: str, status: str = "done"):
        """Update the most recent step with its result."""
        if self.current_steps:
            self.current_steps[-1].result = result
            self.current_steps[-1].status = status

    async def run_workflow(self):
        """Trigger CrewAI crew with current_input."""
        self.is_loading = True
        self.current_status = "running"
        self.current_steps = []
        # → calls orchestrator.run_crew(self.current_input, state_callback=self.add_step)

    def reset_workflow(self):
        """Clear current workflow state."""
        self.current_input = ""
        self.current_steps = []
        self.current_status = "idle"
        self.error_message = ""
```

### Memory Layer (memory.py)
```python
class MemoryManager:
    """
    Manages context passing between agents.
    In v1: wraps CrewAI built-in memory.
    In v2: will add SQLite persistence.
    """

    def __init__(self):
        self.session_context = {}

    def store(self, key: str, value: Any):
        """Store a result for cross-agent access."""
        self.session_context[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }

    def retrieve(self, key: str) -> Any:
        """Retrieve stored context."""
        item = self.session_context.get(key)
        return item["value"] if item else None

    def summarize_for_context(self, max_tokens: int = 2000) -> str:
        """
        Summarize session context to stay within LLM token limits.
        Simple truncation in v1 — smarter summarization in v2.
        """
        context_str = str(self.session_context)
        if len(context_str) > max_tokens * 4:  # rough char estimate
            # Keep most recent entries only
            recent = dict(list(self.session_context.items())[-5:])
            return f"[Context truncated] Recent context: {str(recent)}"
        return context_str

    def clear(self):
        """Clear context at end of workflow."""
        self.session_context = {}
```

### CrewAI Memory Config
```python
# In orchestrator.py — enable CrewAI built-in memory
crew = Crew(
    ...
    memory=True,          # Enable short-term memory
    verbose=True,
    # future: long_term_memory=SQLiteStorage("./memory.db")
)
```

---

## Integration Notes
- `AppState` is the **central state** — all modules read/write from it via Reflex
- `MemoryManager` is instantiated once per workflow run by the orchestrator
- This module **is called by** orchestrator when storing/retrieving cross-agent results
- UI reads `AppState.current_steps` to render the live workflow log
