"""Central configuration for Vision Lens."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM Provider ---
# Supported: "deepseek", "anthropic", "openai", "google", "moonshot", "zhipu", "qwen", "mistral", "xai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").lower()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# OpenAI-compatible (generic)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# --- Provider config mapping ---
_PROVIDER_CONFIG = {
    "deepseek":  {"model": "deepseek/deepseek-chat",           "base_url": "https://api.deepseek.com"},
    "anthropic": {"model": "anthropic/claude-sonnet-4-6",       "base_url": "https://api.anthropic.com"},
    "openai":    {"model": "openai/gpt-4o",                    "base_url": "https://api.openai.com/v1"},
    "google":    {"model": "gemini-2.5-flash",                 "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/"},
    "moonshot":  {"model": "moonshot-v1-8k",                   "base_url": "https://api.moonshot.cn/v1"},
    "zhipu":     {"model": "glm-4-plus",                       "base_url": "https://open.bigmodel.cn/api/paas/v4"},
    "qwen":      {"model": "qwen-max",                         "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    "mistral":   {"model": "mistral/mistral-large-latest",      "base_url": "https://api.mistral.ai/v1"},
    "xai":       {"model": "grok-3-beta",                      "base_url": "https://api.x.ai/v1"},
}

# --- LLM Configuration (derived) ---
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")

if LLM_PROVIDER in _PROVIDER_CONFIG:
    cfg = _PROVIDER_CONFIG[LLM_PROVIDER]
    LLM_MODEL = LLM_MODEL or cfg["model"]
    LLM_BASE_URL = LLM_BASE_URL or cfg["base_url"]

# Per-provider API key fallback
if not LLM_API_KEY:
    if LLM_PROVIDER == "deepseek":
        LLM_API_KEY = DEEPSEEK_API_KEY
    elif LLM_PROVIDER == "openai":
        LLM_API_KEY = OPENAI_API_KEY
    elif LLM_PROVIDER == "anthropic":
        LLM_API_KEY = ANTHROPIC_API_KEY

IS_LLM_CONFIGURED = bool(LLM_API_KEY)


def _get_llm_config(session_key_prefix: str) -> dict:
    """Read LLM config from Streamlit session state, falling back to env vars."""
    try:
        import streamlit as st
        provider = st.session_state.get(f"{session_key_prefix}_provider")
        if provider:
            model = st.session_state.get(f"{session_key_prefix}_model", "")
            api_key = st.session_state.get(f"{session_key_prefix}_api_key", "")
            base_url = st.session_state.get(f"{session_key_prefix}_base_url", "")
            if model and api_key:
                # If model has no provider prefix, force openai provider for custom endpoints
                llm_provider = None if "/" in model else "openai"
                return {"model": model, "api_key": api_key, "base_url": base_url, "llm_provider": llm_provider}
    except Exception:
        pass
    # Fallback: detect provider from env model format
    env_provider = None if "/" in LLM_MODEL else "openai"
    return {"model": LLM_MODEL, "api_key": LLM_API_KEY, "base_url": LLM_BASE_URL, "llm_provider": env_provider}


def create_llm(temperature: float = 0.1):
    """Create a CrewAI LLM instance from current config. Single factory for all LLM calls."""
    from crewai import LLM
    kwargs = dict(model=LLM_MODEL, api_key=LLM_API_KEY, temperature=temperature)
    if LLM_BASE_URL:
        kwargs["base_url"] = LLM_BASE_URL
    return LLM(**kwargs)


def create_search_llm(temperature: float = 0.1):
    """Create LLM for search/collection tasks (Scout agent, relevance filters)."""
    from crewai import LLM
    cfg = _get_llm_config("search_llm")
    kwargs = dict(model=cfg["model"], api_key=cfg["api_key"], temperature=temperature)
    if cfg["base_url"]:
        kwargs["base_url"] = cfg["base_url"]
    if cfg.get("llm_provider"):
        kwargs["provider"] = cfg["llm_provider"]
    return LLM(**kwargs)


def create_integration_llm(temperature: float = 0.1):
    """Create LLM for analysis/integration tasks (Challenger, Judge, Editor, Q&A)."""
    from crewai import LLM
    cfg = _get_llm_config("integration_llm")
    kwargs = dict(model=cfg["model"], api_key=cfg["api_key"], temperature=temperature)
    if cfg["base_url"]:
        kwargs["base_url"] = cfg["base_url"]
    if cfg.get("llm_provider"):
        kwargs["provider"] = cfg["llm_provider"]
    return LLM(**kwargs)


def is_search_llm_configured() -> bool:
    return bool(_get_llm_config("search_llm")["api_key"])


def is_integration_llm_configured() -> bool:
    return bool(_get_llm_config("integration_llm")["api_key"])


def get_active_domains() -> list[str] | None:
    """Return active search domains, or None for unrestricted.
    Reads from Streamlit session state if available, else returns defaults.
    """
    # Try Streamlit context first
    try:
        import streamlit as st
        if "search_domains" in st.session_state:
            if st.session_state.get("search_unrestricted", False):
                return None
            domains = [d for d in st.session_state.search_domains.values()]
            if domains:
                return domains
    except Exception:
        pass
    # Fallback to defaults
    return list(DEFAULT_SEARCH_DOMAINS.values())

# --- Search ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Default search domains (name -> domain)
DEFAULT_SEARCH_DOMAINS = {
    "知乎": "zhihu.com",
    "微博": "weibo.com",
    "搜狐": "sohu.com",
    "新浪": "sina.com.cn",
    "网易": "163.com",
    "腾讯": "qq.com",
    "澎湃新闻": "thepaper.cn",
    "凤凰网": "ifeng.com",
    "观察者网": "guancha.cn",
    "财新": "caixin.com",
    "BBC": "bbc.com",
    "CNN": "cnn.com",
    "路透社": "reuters.com",
    "美联社": "apnews.com",
    "纽约时报": "nytimes.com",
    "卫报": "theguardian.com",
    "华盛顿邮报": "washingtonpost.com",
}

# --- Paths ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- UI ---
APP_TITLE = "AI资讯透视镜 Vision Lens"
APP_ICON = "🔍"
APP_LAYOUT = "wide"
