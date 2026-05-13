"""Workflow orchestration for Libra AI Coworker.

The module configures CrewAI-compatible agents and runs a deterministic demo
pipeline that is safe to execute in local/dev environments. This keeps the
product demo responsive over SSE while preserving the same agent and tool
boundaries used for a live LLM-backed CrewAI implementation.
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any

from state.workflow_manager import WorkflowSession
from tools.crm_tool import _send_email_draft_impl, _update_crm_impl, send_email_draft, update_crm
from tools.gmail_tool import _search_gmail_impl, search_gmail
from tools.slack_tool import _search_slack_impl, search_slack

try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover
    ChatOpenAI = None  # type: ignore[assignment]

try:
    from crewai import Agent, Crew, Process, Task
except Exception:  # pragma: no cover
    Agent = Crew = Process = Task = None  # type: ignore[assignment]


MODEL = os.getenv("NVIDIA_MODEL", "zhipuai/glm-4v-flash")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

SAFETY_SYSTEM_PROMPT = """
CRITICAL SAFETY RULES:
1. You MUST NEVER execute write operations (update CRM, send emails, post to Slack)
   without explicit user approval.
2. Before any write action, always call the approval check first.
3. If the user rejects an action, acknowledge it and do not retry the same action.
4. Always clearly describe what you are about to do BEFORE doing it.
5. When in doubt, ask for clarification rather than assuming.
"""


@dataclass(frozen=True)
class PlannedWrite:
    tool: str
    description: str
    parameters: dict[str, Any]


def get_llm() -> Any:
    """Return the NVIDIA-hosted GLM LLM client for CrewAI."""

    if ChatOpenAI is None:
        raise RuntimeError("langchain-openai is not installed")
    return ChatOpenAI(
        model=MODEL,
        openai_api_base=NVIDIA_BASE_URL,
        openai_api_key=os.environ.get("NVIDIA_API_KEY", ""),
        temperature=0.1,
    )


def create_crew_blueprint(user_input: str) -> Any | None:
    """Build a CrewAI crew object for production parity.

    The current API path uses a deterministic runner for reliable SSE demos. This
    blueprint is kept isolated so enabling live CrewAI kickoff later is a small
    change rather than a rewrite.
    """

    if not all([Agent, Crew, Process, Task, ChatOpenAI]):
        return None
    if any(
        getattr(tool_obj, "_libra_fallback_tool", False)
        for tool_obj in [search_gmail, search_slack, update_crm, send_email_draft]
    ):
        return None

    llm = get_llm()
    researcher = Agent(
        role="Researcher",
        goal="Gather relevant context from Gmail and Slack for the user request.",
        backstory=f"Meticulous enterprise researcher. {SAFETY_SYSTEM_PROMPT}",
        tools=[search_gmail, search_slack],
        llm=llm,
        verbose=True,
        max_iter=3,
        allow_delegation=False,
    )
    analyst = Agent(
        role="Analyst",
        goal="Turn raw research into concise decisions and recommended actions.",
        backstory=f"Business analyst who writes clear, actionable summaries. {SAFETY_SYSTEM_PROMPT}",
        tools=[],
        llm=llm,
        verbose=True,
        max_iter=2,
        allow_delegation=False,
    )
    executor = Agent(
        role="Executor",
        goal="Execute approved CRM and email draft actions safely.",
        backstory=f"Careful operator who never performs writes without approval. {SAFETY_SYSTEM_PROMPT}",
        tools=[update_crm, send_email_draft],
        llm=llm,
        verbose=True,
        max_iter=3,
        allow_delegation=False,
    )
    research_task = Task(
        description=f"Research Gmail and Slack for this request: {user_input}",
        expected_output="Structured research summary with emails, Slack messages, people, and companies.",
        agent=researcher,
    )
    analysis_task = Task(
        description="Synthesize the research into key findings and recommended actions.",
        expected_output="Concise analysis with specific recommended next steps.",
        agent=analyst,
        context=[research_task],
    )
    execution_task = Task(
        description="Execute only approved write actions and return a final report.",
        expected_output="Final execution report with completed and skipped actions.",
        agent=executor,
        context=[research_task, analysis_task],
    )
    return Crew(
        agents=[researcher, analyst, executor],
        tasks=[research_task, analysis_task, execution_task],
        process=Process.sequential,
        memory=True,
        verbose=True,
    )


def _infer_query(user_input: str) -> str:
    candidates = ["Acme Corp", "TechCorp", "Nexus Solutions", "StartupCo", "sales", "lead"]
    lower_input = user_input.lower()
    for candidate in candidates:
        if candidate.lower() in lower_input:
            return candidate
    return user_input[:80]


def _infer_channel(user_input: str) -> str:
    words = user_input.split()
    for word in words:
        if word.startswith("#") and len(word) > 1:
            return word
    return "#sales"


def _load_json(raw: str) -> dict[str, Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def _analyze(user_input: str, gmail: dict[str, Any], slack: dict[str, Any]) -> str:
    emails = gmail.get("emails", [])
    messages = slack.get("messages", [])
    company = "the account"
    if emails:
        company = emails[0].get("company", company)
    elif messages:
        first_words = messages[0].get("text", "").split()
        company = " ".join(first_words[:2]) if first_words else company

    findings = [
        f"{len(emails)} relevant Gmail thread(s) and {len(messages)} Slack message(s) were found.",
        f"{company} appears active and needs a clear next step captured.",
        "Approval-gated write actions are required only when the request asks for CRM updates or email drafts.",
    ]
    if "digest" in user_input.lower() or "summarize" in user_input.lower():
        findings.append("The safest output is a written digest unless the user explicitly asks for a write action.")

    return "\n".join(f"- {finding}" for finding in findings)


def _plan_writes(user_input: str, analysis: str, gmail: dict[str, Any]) -> list[PlannedWrite]:
    lower_input = user_input.lower()
    emails = gmail.get("emails", [])
    primary = emails[0] if emails else {}
    contact_name = str(primary.get("from", "Sarah Chen <sarah.chen@acmecorp.com>")).split("<")[0].strip()
    company = primary.get("company", "Acme Corp")

    writes: list[PlannedWrite] = []
    if "crm" in lower_input or "note" in lower_input or "update" in lower_input:
        note = (
            f"{company} status: active evaluation. {analysis.replace(chr(10), ' ')} "
            "Recommended follow-up: confirm business owner, security requirements, and next meeting date."
        )
        writes.append(
            PlannedWrite(
                tool="update_crm",
                description=f"Update CRM record for {contact_name} at {company}.",
                parameters={"contact_name": contact_name, "note": note},
            )
        )

    if "email" in lower_input or "draft" in lower_input or "outreach" in lower_input:
        to = "james.wilson@techcorp.io" if "techcorp" in lower_input else "sarah.chen@acmecorp.com"
        subject = "Follow-up on next steps"
        body = (
            "Hi,\n\n"
            "Thanks for the recent discussion. I pulled together the current status and suggested next steps. "
            "The main items are security review, commercial alignment, and scheduling the next working session.\n\n"
            "Would Tuesday afternoon work for a 30-minute follow-up?\n\n"
            "Best,\nLibra AI"
        )
        writes.append(
            PlannedWrite(
                tool="send_email_draft",
                description=f"Create a follow-up email draft to {to}.",
                parameters={"to": to, "subject": subject, "body": body},
            )
        )

    return writes


async def run_workflow(session: WorkflowSession) -> None:
    """Run a workflow and emit each step into the session SSE queue."""

    try:
        user_input = session.user_input
        create_crew_blueprint(user_input)
        query = _infer_query(user_input)
        channel = _infer_channel(user_input)

        await session.emit("Manager", "Received request and decomposed work across Researcher, Analyst, and Executor.", "running")
        await asyncio.sleep(0.15)
        await session.emit("Manager", "Task plan ready: research context, synthesize findings, then gate any writes.", "done")

        await session.emit("Researcher", f"Searching Gmail for '{query}' across recent account threads.", "running")
        await asyncio.sleep(0.2)
        gmail_raw = _search_gmail_impl(query=query, days=7)
        gmail = _load_json(gmail_raw)
        await session.emit("Researcher", "Gmail research complete.", "done", result=gmail_raw)

        await session.emit("Researcher", f"Searching Slack channel {channel} for matching context.", "running")
        await asyncio.sleep(0.2)
        slack_raw = _search_slack_impl(channel=channel, query=query)
        slack = _load_json(slack_raw)
        await session.emit("Researcher", "Slack research complete.", "done", result=slack_raw)

        await session.emit("Analyst", "Synthesizing research into account status and recommended next steps.", "running")
        await asyncio.sleep(0.25)
        analysis = _analyze(user_input, gmail, slack)
        await session.emit("Analyst", "Analysis complete.", "done", result=analysis)

        writes = _plan_writes(user_input, analysis, gmail)
        execution_results: list[str] = []
        if not writes:
            await session.emit(
                "Executor",
                "No write action was requested, so the workflow will return a digest without external changes.",
                "done",
                result="No approval needed. No CRM record or email draft was changed.",
            )

        for write in writes:
            decision = await session.request_approval(write.tool, write.description, write.parameters)
            if decision == "rejected":
                message = f"User rejected {write.tool}; action skipped and workflow continued."
                execution_results.append(message)
                await session.emit("Executor", message, "done")
                continue

            await session.emit("Executor", f"Approval received. Executing {write.tool}.", "running")
            await asyncio.sleep(0.2)
            if write.tool == "update_crm":
                result = _update_crm_impl(**write.parameters)
            else:
                result = _send_email_draft_impl(**write.parameters)
            execution_results.append(result)
            await session.emit("Executor", f"{write.tool} completed after approval.", "done", result=result)

        final_result = "\n\n".join(
            [
                "### Workflow Summary",
                analysis,
                "### Execution",
                "\n".join(execution_results) if execution_results else "No write actions were required.",
            ]
        )
        await session.finish(final_result=final_result, status="complete")
    except Exception as exc:
        await session.finish(
            final_result=f"The workflow stopped safely because an internal error occurred: {exc}",
            status="error",
        )


__all__ = ["MODEL", "NVIDIA_BASE_URL", "run_workflow", "get_llm", "create_crew_blueprint"]
