"""Agent factory utilities for Vision Lens."""

from crewai import LLM
from config import LLM_MODEL, LLM_API_KEY, LLM_BASE_URL


def create_llm(temperature: float = 0.1) -> LLM:
    """Create a CrewAI LLM instance based on the configured provider."""
    kwargs = dict(
        model=LLM_MODEL,
        api_key=LLM_API_KEY,
        temperature=temperature,
    )
    if LLM_BASE_URL:
        kwargs["base_url"] = LLM_BASE_URL
    return LLM(**kwargs)
