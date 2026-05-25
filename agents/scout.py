"""Scout Agent — Multi-source intelligence gathering."""

from crewai import Agent
from tools.search_tool import TruthLensSearchTool
from agents import create_search_llm
from utils.i18n import t


def create_scout_agent() -> Agent:
    """Create the Scout Agent responsible for gathering multi-source intel."""

    return Agent(
        role=t("agent.scout.role"),
        goal=t("agent.scout.goal"),
        backstory=t("agent.scout.backstory"),
        tools=[TruthLensSearchTool()],
        llm=create_search_llm(temperature=0.1),
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )
