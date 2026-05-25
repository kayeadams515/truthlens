"""Judge Agent — Bayesian truth probability scoring."""

from crewai import Agent
from agents import create_integration_llm
from utils.i18n import t


def create_judge_agent() -> Agent:
    """Create the Judge Agent — logical scoring based on evidence chain completeness."""

    return Agent(
        role=t("agent.judge.role"),
        goal=t("agent.judge.goal"),
        backstory=t("agent.judge.backstory"),
        llm=create_integration_llm(temperature=0.1),
        verbose=True,
        allow_delegation=False,
    )
