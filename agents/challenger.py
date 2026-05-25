"""Challenger Agent — Adversarial cross-examination."""

from crewai import Agent
from agents import create_integration_llm
from utils.i18n import t


def create_challenger_agent() -> Agent:
    """Create the Challenger Agent — the adversarial skeptic."""

    return Agent(
        role=t("agent.challenger.role"),
        goal=t("agent.challenger.goal"),
        backstory=t("agent.challenger.backstory"),
        llm=create_integration_llm(temperature=0.3),
        verbose=True,
        allow_delegation=False,
    )
