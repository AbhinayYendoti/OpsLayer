# Module PRD: Agent Orchestration

## Module Owner
Agent Orchestration Specialist Agent

## Version
`v1.0`

---

## Objective
Build a reliable multi-agent orchestration system using CrewAI that can receive a natural
language task, decompose it into steps, delegate to the right agents, and return a structured
result with full step logging.

---

## Scope
This module owns:
- `/libra_app/agents/orchestrator.py`
- `/libra_app/agents/researcher.py`
- `/libra_app/agents/analyst.py`
- `/libra_app/agents/executor.py`

**Do NOT touch:** UI components, tool implementations, state management, safety checks.

---

## Agent Roles

### Manager Agent (Orchestrator)
- **Goal:** Decompose user request into a clear task list and delegate to the right agent
- **Backstory:** Expert project manager who breaks complex requests into simple subtasks
- **Process:** Hierarchical — manages the crew

### Researcher Agent
- **Goal:** Gather relevant information from available tools (Gmail, Slack)
- **Backstory:** Detail-oriented researcher who finds exactly the right information
- **Tools:** `search_gmail`, `search_slack`
- **Output:** Structured data summary

### Analyst Agent
- **Goal:** Synthesize raw data into clear, actionable insights
- **Backstory:** Data analyst who turns raw information into clear recommendations
- **Tools:** None (reasoning only)
- **Output:** Analysis summary, recommended actions

### Executor Agent
- **Goal:** Execute approved write actions safely and report results
- **Backstory:** Careful executor who always confirms before taking action
- **Tools:** `update_crm`, `send_email_draft`
- **Output:** Confirmation of completed actions

---

## Acceptance Criteria

| # | Criteria | Test |
|---|----------|------|
| 1 | Manager correctly decomposes a multi-step request | Pass 3 test workflows |
| 2 | Tasks are assigned to the correct specialized agent | Check agent logs |
| 3 | Each agent produces structured output | Validate output schema |
| 4 | All steps are logged with timestamps | Check logger output |
| 5 | Crew completes end-to-end without crashing | Integration test pass |
| 6 | Basic retry on tool failure (max 2 retries) | Simulate tool error |

---

## Technical Specifications

### Framework
```
CrewAI — hierarchical process
Manager → delegates Tasks to Agents → Agents use Tools → Results aggregated
```

### Agent Config Pattern
```python
from crewai import Agent, Task, Crew, Process

researcher = Agent(
    role="Research Specialist",
    goal="Find relevant information from Gmail and Slack",
    backstory="...",
    tools=[search_gmail, search_slack],
    verbose=True,
    max_iter=3
)
```

### Task Config Pattern
```python
research_task = Task(
    description="Search Gmail for emails from {contact} in the last {days} days",
    expected_output="List of relevant emails with subject, sender, date, summary",
    agent=researcher
)
```

### Crew Config Pattern
```python
crew = Crew(
    agents=[researcher, analyst, executor],
    tasks=[research_task, analysis_task, execution_task],
    process=Process.hierarchical,
    manager_llm=ChatOpenAI(model="gpt-4o"),
    verbose=True
)
```

### Step Logging
- Every agent action → emit to `AppState.workflow_steps` list
- Format: `{"step": N, "agent": "Researcher", "action": "...", "status": "running|done|error", "timestamp": "..."}`

---

## Test Workflows (Acceptance Tests)

### Workflow 1: CRM Update from Gmail
```
Input: "Find emails from Acme Corp this week and add a CRM note"
Expected: Researcher finds emails → Analyst summarizes → Executor updates CRM (after approval)
```

### Workflow 2: Slack Digest
```
Input: "Summarize today's #sales channel and send me a brief"
Expected: Researcher reads Slack → Analyst writes digest → displayed in UI
```

### Workflow 3: Lead Research
```
Input: "Research John Smith at TechCorp and prepare an outreach summary"
Expected: Researcher gathers info → Analyst prepares brief → Executor drafts email (after approval)
```

---

## Integration Notes
- This module is **called by** `AppState` in `/libra_app/state/app_state.py`
- This module **calls** tools from `/libra_app/tools/`
- This module **emits** step events to `AppState.workflow_steps`
- Safety checks are handled by the Safety module — do not duplicate
