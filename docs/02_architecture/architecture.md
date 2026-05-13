# Architecture Document: Libra AI Coworker Demo

## Version
`v1.0`

---

## High-Level Architecture

```
User Input (Natural Language)
        │
        ▼
┌─────────────────────────────┐
│   Reflex Frontend (UI)      │  ← Notion-style interface
│   sidebar + workflow logs   │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   CrewAI Manager Agent      │  ← Task decomposition & planning
│   (Orchestrator)            │
└──┬──────────────────────────┘
   │         │          │
   ▼         ▼          ▼
┌──────┐ ┌────────┐ ┌──────────┐
│Research│ │Analyst │ │Executor  │  ← Specialized agents
│Agent  │ │Agent   │ │Agent     │
└──┬───┘ └───┬────┘ └────┬─────┘
   │         │           │
   └─────────┴─────┬─────┘
                   ▼
        ┌──────────────────┐
        │   Tools Layer    │
        │  Gmail | Slack   │
        │  CRM | Search    │
        └──────┬───────────┘
               │
        ┌──────▼───────────┐
        │  Safety Layer    │  ← Human approval for writes
        │  (HITL Check)    │
        └──────┬───────────┘
               │
        ┌──────▼───────────┐
        │  Results / Logs  │  ← Back to UI
        └──────────────────┘
```

---

## Core Components

### 1. UI Layer — Reflex Frontend
- **Location:** `/libra_app/`
- **Framework:** Reflex (Python → React compilation)
- **Style:** Notion-inspired: clean cards, sidebar, dark mode
- **Key Views:**
  - Sidebar (navigation + history)
  - Workflow Input Panel
  - Live Step Log
  - Approval Dialog
  - Results Summary

### 2. Orchestration Layer — CrewAI Manager
- **Location:** `/libra_app/agents/orchestrator.py`
- **Role:** Receives user input → decomposes into tasks → assigns to agents
- **Process:** Hierarchical (Manager delegates to agents)
- **Logging:** Emits step events back to Reflex state

### 3. Agent Layer — Specialized Agents
| Agent | Role | Tools Access |
|-------|------|-------------|
| Researcher | Gathers data from Gmail/Slack | search_gmail, search_slack |
| Analyst | Synthesizes info, produces insights | (analysis, no write) |
| Executor | Executes write actions with approval | update_crm, send_email |

### 4. Tools Layer — Mock Integrations
- **Location:** `/libra_app/tools/`
- **Pattern:** All tools use CrewAI `@tool` decorator
- **Mock Strategy:** Realistic fake responses with TODO comments for real APIs
- **Tools:**
  - `search_gmail()` — searches inbox mock
  - `search_slack()` — searches channel mock
  - `update_crm()` — updates CRM record (requires approval)
  - `send_email_draft()` — creates draft (requires approval)

### 5. Safety Layer — Human-in-the-Loop
- **Location:** `/libra_app/state/safety.py`
- **Rule:** Any tool marked `requires_approval=True` → pauses workflow
- **UI:** Modal dialog shows action summary → user approves / rejects
- **Never bypassed**, even in test mode

### 6. Memory & Context Layer
- **Location:** `/libra_app/state/memory.py`
- **Strategy:** CrewAI built-in memory + Reflex session state
- **Scope:** Per-workflow session (not persistent across sessions in v1)

---

## Data Flow — Step by Step

```
1. User types: "Check my Gmail for leads from last week
                and update CRM with a summary"

2. Reflex State receives input → triggers crew kickoff

3. Manager Agent decomposes:
   Task A → Researcher: search_gmail(query="leads", days=7)
   Task B → Analyst: summarize findings
   Task C → Executor: update_crm(data=summary) ← APPROVAL REQUIRED

4. Tasks execute sequentially / in parallel per CrewAI plan

5. Step B: Executor pauses → Reflex shows approval modal
   User reviews summary → Approves

6. CRM update executes → mock response returned

7. Final summary displayed in workflow log
```

---

## Folder Structure

```
libra_ai_coworker/
├── docs/
│   ├── 01_master_prd/
│   │   └── master_prd.md
│   ├── 02_architecture/
│   │   └── architecture.md
│   └── 03_module_prds/
│       ├── agent_orchestration.md
│       ├── tool_integrations.md
│       ├── safety_and_guardrails.md
│       ├── memory_and_context.md
│       └── user_interface.md
│
├── libra_app/                   ← Main Reflex application
│   ├── libra_app.py             ← App entry point
│   ├── components/              ← Reusable UI components
│   │   ├── sidebar.py
│   │   ├── workflow_log.py
│   │   ├── approval_modal.py
│   │   └── result_card.py
│   ├── agents/                  ← CrewAI agents
│   │   ├── orchestrator.py      ← Manager + Crew setup
│   │   ├── researcher.py
│   │   ├── analyst.py
│   │   └── executor.py
│   ├── tools/                   ← Mock tool integrations
│   │   ├── gmail_tool.py
│   │   ├── slack_tool.py
│   │   └── crm_tool.py
│   ├── state/                   ← Reflex global state
│   │   ├── app_state.py
│   │   ├── safety.py
│   │   └── memory.py
│   └── utils/
│       └── logger.py
│
├── tests/
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_workflows.py
│
├── .env.example
├── requirements.txt
├── rxconfig.py
└── README.md
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Reflex for frontend | Python-native, no separate JS codebase needed |
| CrewAI hierarchical process | Clean manager-agent pattern, easy to read |
| Mock tools first | Ship fast, replace with real APIs later |
| Approval before all writes | Safety is non-negotiable for enterprise trust |
| Modular folder structure | Easy to hand off to specialized agents in parallel |

---

## Future Scalability Path

```
v1 (Now)              v2                    v3
Mock tools     →   Real OAuth APIs    →   RAG over company data
CrewAI         →   LangGraph          →   Custom eval framework
Session memory →   SQLite/Postgres    →   Vector DB (Pinecone)
Single user    →   Multi-user         →   Teams + permissions
```
