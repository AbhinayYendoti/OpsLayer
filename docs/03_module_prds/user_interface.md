# Module PRD: User Interface

## Module Owner
Frontend Specialist Agent

## Version
`v1.0`

---

## Objective
Build a clean, professional, Notion-inspired UI using Reflex (Python → React).
The UI must feel like a premium enterprise tool — not a demo project.
Every interaction should give live feedback on what the AI is doing.

---

## Scope
This module owns:
- `/libra_app/libra_app.py` — Main app entry point
- `/libra_app/components/sidebar.py`
- `/libra_app/components/workflow_log.py`
- `/libra_app/components/approval_modal.py`
- `/libra_app/components/result_card.py`
- `/rxconfig.py`

**Do NOT touch:** Agent logic, tools, state logic (except reading from AppState).

---

## Design Principles
- **Clean over flashy** — Notion, Linear, Vercel-inspired aesthetics
- **Information density** — show what's happening without clutter
- **Trust-building** — every AI action is visible and logged
- **Dark mode first** — dark background, muted grays, clean whites

---

## Screen Layout

```
┌─────────────────────────────────────────────────────────┐
│  SIDEBAR (240px)        │  MAIN CONTENT AREA            │
│                         │                               │
│  🤖 Libra AI            │  ┌─────────────────────────┐  │
│  ─────────────          │  │  WORKFLOW INPUT          │  │
│  + New Workflow         │  │  ┌──────────────────┐   │  │
│                         │  │  │ What should I    │   │  │
│  Recent:                │  │  │ do for you?      │   │  │
│  • CRM Update           │  │  └──────────────────┘   │  │
│  • Slack Digest         │  │  [Run Workflow ▶]        │  │
│  • Lead Research        │  └─────────────────────────┘  │
│                         │                               │
│  ─────────────          │  ┌─────────────────────────┐  │
│  ⚙ Settings             │  │  LIVE WORKFLOW LOG       │  │
│  📖 Docs                │  │                          │  │
│                         │  │  ✅ Step 1: Researcher   │  │
│                         │  │     Searching Gmail...   │  │
│                         │  │                          │  │
│                         │  │  🔄 Step 2: Analyst      │  │
│                         │  │     Analyzing results... │  │
│                         │  │                          │  │
│                         │  │  ⏳ Step 3: Executor      │  │
│                         │  │     Waiting approval...  │  │
│                         │  └─────────────────────────┘  │
│                         │                               │
│                         │  ┌─────────────────────────┐  │
│                         │  │  RESULT CARD             │  │
│                         │  │  (appears when done)     │  │
│                         │  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Sidebar (`sidebar.py`)
- Fixed 240px width
- App logo/name at top: "🤖 Libra AI"
- "+ New Workflow" button (prominent)
- List of recent workflow runs from `AppState.workflow_history`
  - Each item: icon + truncated input text
  - Hover: subtle highlight
- Bottom: Settings, Docs links
- Styling: `#1a1a1a` background, `#2a2a2a` hover

### 2. Workflow Input Panel (`libra_app.py` main area)
- Large, clean text area: `"What workflow should I run?"` placeholder
- Character counter (max 500)
- [▶ Run Workflow] button — disabled while running
- Shows spinner when `AppState.is_loading`

### 3. Workflow Log (`workflow_log.py`)
- Renders `AppState.current_steps` as a vertical timeline
- Each step is a card showing:
  - Step number badge
  - Agent name (color-coded: Researcher=blue, Analyst=purple, Executor=orange)
  - Action description
  - Status icon: 🔄 running / ✅ done / ❌ error / ⏳ waiting
  - Expandable result area
  - Timestamp (right-aligned)
- Live updates as new steps arrive
- Auto-scrolls to latest step

### 4. Approval Modal (`approval_modal.py`)
- Triggered when `SafetyState.show_approval_modal = True`
- Overlay with blur background
- Shows action details clearly
- [✅ Approve] [✏️ Edit] [❌ Reject] buttons
- Cannot be closed by clicking outside (must make a decision)

### 5. Result Card (`result_card.py`)
- Appears when `AppState.current_status == "complete"`
- Clean card with final summary
- Markdown rendering support
- [📋 Copy] [🔄 Run Again] buttons

---

## Acceptance Criteria

| # | Criteria |
|---|----------|
| 1 | Sidebar renders with navigation and recent history |
| 2 | Workflow input submits and triggers agent run |
| 3 | Live log updates in real-time as steps complete |
| 4 | Agent colors and status icons are consistent |
| 5 | Approval modal blocks workflow until decision made |
| 6 | Result card renders markdown correctly |
| 7 | Dark mode is default and looks polished |
| 8 | App is responsive (works at 1200px+ width) |

---

## Color Palette
```python
COLORS = {
    "background": "#111111",
    "surface": "#1a1a1a",
    "surface_hover": "#222222",
    "border": "#2a2a2a",
    "text_primary": "#e5e5e5",
    "text_secondary": "#888888",
    "accent_blue": "#3b82f6",
    "accent_purple": "#8b5cf6",
    "accent_orange": "#f97316",
    "accent_green": "#22c55e",
    "accent_red": "#ef4444",
    # Agent colors
    "agent_researcher": "#3b82f6",
    "agent_analyst": "#8b5cf6",
    "agent_executor": "#f97316",
    "agent_manager": "#22c55e",
}
```

## Typography
```python
FONTS = {
    "sans": "Inter, -apple-system, sans-serif",
    "mono": "JetBrains Mono, Fira Code, monospace",
    "heading_size": "1.5rem",
    "body_size": "0.875rem",
    "small_size": "0.75rem",
}
```

---

## Reflex-Specific Notes
```python
# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name="libra_app",
    frontend_port=3000,
    backend_port=8000,
)
```

```python
# Main app entry: libra_app.py
import reflex as rx
from .components.sidebar import sidebar
from .components.workflow_log import workflow_log
from .components.approval_modal import approval_modal
from .components.result_card import result_card
from .state.app_state import AppState

def index() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            # main content
            workflow_input_panel(),
            workflow_log(),
            result_card(),
        ),
        approval_modal(),  # always rendered, hidden by default
    )

app = rx.App()
app.add_page(index, route="/")
```

---

## Integration Notes
- This module **reads from** `AppState` and `SafetyState` — never writes directly to agent logic
- The `approval_modal` component **calls** `SafetyState.approve_action()` and `SafetyState.reject_action()`
- Workflow log auto-updates because it's bound to `AppState.current_steps` (Reflex reactive state)
