"""
libra_app/agents/orchestrator.py
==================================
CrewAI multi-agent orchestrator for Libra AI Coworker Demo.
Manages the Manager → Researcher → Analyst → Executor pipeline.
"""

import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from libra_app.tools.gmail_tool import search_gmail
from libra_app.tools.slack_tool import search_slack
from libra_app.tools.crm_tool import update_crm, send_email_draft

load_dotenv()

# ============================================================
# Safety System Prompt (injected into all agents)
# ============================================================

SAFETY_PROMPT = """
CRITICAL SAFETY RULES — NEVER VIOLATE:
1. NEVER call update_crm or send_email_draft without first confirming the action summary with the user.
2. Before executing ANY write action, clearly state what you are about to do and why.
3. If the user rejects an action, acknowledge it and move on — do not retry.
4. Be transparent: always explain your reasoning at each step.
5. When uncertain, ask for clarification rather than making assumptions.
"""


# ============================================================
# LLM Configuration
# ============================================================

def get_llm(temperature: float = 0.1):
    """Get the configured LLM instance."""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


# ============================================================
# Agent Definitions
# ============================================================

def create_researcher(llm) -> Agent:
    """
    Researcher Agent — gathers information from Gmail and Slack.
    Read-only: does not take any write actions.
    """
    return Agent(
        role="Research Specialist",
        goal=(
            "Find all relevant information from Gmail and Slack that is needed "
            "to complete the user's request. Be thorough and specific."
        ),
        backstory=(
            "You are a meticulous research specialist with years of experience "
            "finding the right information quickly. You search Gmail for emails "
            "and Slack for team conversations. You present findings clearly and "
            "include all relevant details (names, dates, context). "
            + SAFETY_PROMPT
        ),
        tools=[search_gmail, search_slack],
        llm=llm,
        verbose=True,
        max_iter=3,
        allow_delegation=False,
    )


def create_analyst(llm) -> Agent:
    """
    Analyst Agent — synthesizes information into clear insights.
    No tools needed — reasoning only.
    """
    return Agent(
        role="Information Analyst",
        goal=(
            "Analyze the research findings and produce a clear, structured summary "
            "with actionable insights and specific recommendations."
        ),
        backstory=(
            "You are a sharp analytical thinker who excels at turning raw data "
            "into clear business insights. You identify patterns, highlight key "
            "information, and recommend specific next actions. Your summaries are "
            "concise but complete — executives can act on them immediately. "
            + SAFETY_PROMPT
        ),
        tools=[],  # Analyst uses reasoning only — no external tools
        llm=llm,
        verbose=True,
        max_iter=2,
        allow_delegation=False,
    )


def create_executor(llm) -> Agent:
    """
    Executor Agent — takes write actions after approval.
    Always confirms before executing write operations.
    """
    return Agent(
        role="Action Executor",
        goal=(
            "Execute the approved write actions (CRM updates, email drafts) "
            "carefully and accurately. Always confirm what you're about to do before doing it."
        ),
        backstory=(
            "You are a careful and precise executor who never acts without "
            "explicit authorization. You always describe what you're about to do, "
            "then execute it cleanly. You double-check contact names and details "
            "before updating any systems. "
            + SAFETY_PROMPT
        ),
        tools=[update_crm, send_email_draft],
        llm=llm,
        verbose=True,
        max_iter=3,
        allow_delegation=False,
    )


# ============================================================
# Task Factory
# ============================================================

def create_tasks(user_input: str, researcher: Agent, analyst: Agent, executor: Agent):
    """
    Create the three core tasks based on user input.
    Tasks execute sequentially: Researcher → Analyst → Executor.
    """
    research_task = Task(
        description=(
            f"The user wants: '{user_input}'\n\n"
            "Your job: Search Gmail and Slack to gather ALL relevant information "
            "needed to fulfill this request. \n"
            "- Search Gmail with relevant keywords\n"
            "- Search relevant Slack channels\n"
            "- Collect: names, companies, dates, context, any decisions made\n"
            "- If searching for a specific person or company, search both Gmail and Slack\n"
            "Return a comprehensive, structured summary of everything you found."
        ),
        expected_output=(
            "A structured research report containing:\n"
            "1. Key people and companies identified\n"
            "2. Relevant emails found (subject, sender, date, key points)\n"
            "3. Relevant Slack messages (channel, author, key points)\n"
            "4. Any action items or follow-ups already in progress"
        ),
        agent=researcher,
    )

    analysis_task = Task(
        description=(
            f"Original request: '{user_input}'\n\n"
            "Using the research findings above, produce a clear analysis:\n"
            "- Summarize the key information in 3-5 bullet points\n"
            "- Identify what actions need to be taken\n"
            "- Draft any content needed (CRM notes, email bodies)\n"
            "- Prioritize the actions by importance\n"
            "Be specific: include names, companies, and exact details."
        ),
        expected_output=(
            "An analysis summary containing:\n"
            "1. Key findings (3-5 bullets)\n"
            "2. Recommended actions with specific details\n"
            "3. Drafted content for any write actions needed\n"
            "4. Priority order for execution"
        ),
        agent=analyst,
        context=[research_task],  # Analyst gets researcher's output
    )

    execution_task = Task(
        description=(
            f"Original request: '{user_input}'\n\n"
            "Using the analysis above, execute the approved actions:\n"
            "- For CRM updates: use update_crm() with the contact name and drafted note\n"
            "- For email drafts: use send_email_draft() with the full drafted email\n"
            "IMPORTANT: Before calling any tool, state exactly what you're about to do.\n"
            "If no write actions are needed, just return a summary of what was accomplished."
        ),
        expected_output=(
            "A final execution report containing:\n"
            "1. List of actions taken (or skipped and why)\n"
            "2. Confirmation of each completed action\n"
            "3. A clean final summary for the user"
        ),
        agent=executor,
        context=[research_task, analysis_task],  # Executor gets full context
    )

    return [research_task, analysis_task, execution_task]


# ============================================================
# Main Entry Point
# ============================================================

def run_crew(user_input: str, state=None) -> str:
    """
    Main function: creates and runs the CrewAI crew for a given user input.

    Args:
        user_input: The natural language request from the user
        state: Optional AppState reference for step logging callbacks

    Returns:
        Final result string from the crew execution
    """
    llm = get_llm()

    # Create agents
    researcher = create_researcher(llm)
    analyst = create_analyst(llm)
    executor = create_executor(llm)

    # Log agent creation (if state callback provided)
    if state:
        state.add_step("Manager", "🎯 Task received — decomposing into subtasks", "running")

    # Create tasks
    tasks = create_tasks(user_input, researcher, analyst, executor)

    # Log task assignment
    if state:
        state.update_last_step("Tasks assigned to Researcher → Analyst → Executor", "done")
        state.add_step("Researcher", "🔍 Searching Gmail and Slack for relevant information...", "running")

    # Build and run the crew
    crew = Crew(
        agents=[researcher, analyst, executor],
        tasks=tasks,
        process=Process.sequential,  # Manager → Researcher → Analyst → Executor
        verbose=True,
    )

    # Execute the crew
    result = crew.kickoff(inputs={"user_input": user_input})

    # Log completion
    if state:
        state.add_step("Manager", "✅ Workflow complete", "done")

    return str(result)
