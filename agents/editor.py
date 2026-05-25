"""Editor Agent — Structured report generation."""

from crewai import Agent
from agents import create_integration_llm
from utils.i18n import t


def create_editor_agent() -> Agent:
    """Create the Editor Agent — produces the final structured Markdown report."""

    return Agent(
        role=t("agent.editor.role"),
        goal=t("agent.editor.goal"),
        backstory=t("agent.editor.backstory"),
        llm=create_integration_llm(temperature=0.1),
        verbose=True,
        allow_delegation=False,
    )
