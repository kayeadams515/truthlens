"""Central configuration for Vision Lens."""

import os

# --- Provider config mapping (model defaults & base URLs) ---
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


def _get_llm_config(session_key_prefix: str) -> dict:
    """Read LLM config from Streamlit session state. Returns empty config if unavailable."""
    try:
        import streamlit as st
        provider = st.session_state.get(f"{session_key_prefix}_provider")
        if provider:
            model = st.session_state.get(f"{session_key_prefix}_model", "")
            api_key = st.session_state.get(f"{session_key_prefix}_api_key", "")
            base_url = st.session_state.get(f"{session_key_prefix}_base_url", "")
            if model and api_key:
                llm_provider = None if "/" in model else "openai"
                return {"model": model, "api_key": api_key, "base_url": base_url, "llm_provider": llm_provider}
    except Exception:
        pass
    return {"model": "", "api_key": "", "base_url": "", "llm_provider": None}


def _make_llm_kwargs(cfg: dict, temperature: float) -> dict:
    """Build kwargs dict for CrewAI LLM from config."""
    kwargs = dict(model=cfg["model"], api_key=cfg["api_key"], temperature=temperature)
    if cfg["base_url"]:
        kwargs["base_url"] = cfg["base_url"]
    if cfg.get("llm_provider"):
        kwargs["provider"] = cfg["llm_provider"]
    return kwargs


def create_search_llm(temperature: float = 0.1):
    """Create LLM for Scout agent (info gathering, relevance filtering)."""
    from crewai import LLM
    return LLM(**_make_llm_kwargs(_get_llm_config("search_llm"), temperature))


def create_integration_llm(temperature: float = 0.1):
    """Create LLM for analysis agents (Challenger, Judge, Editor, Q&A)."""
    from crewai import LLM
    return LLM(**_make_llm_kwargs(_get_llm_config("integration_llm"), temperature))


def is_search_llm_configured() -> bool:
    return bool(_get_llm_config("search_llm")["api_key"])


def is_integration_llm_configured() -> bool:
    return bool(_get_llm_config("integration_llm")["api_key"])


def is_any_llm_configured() -> bool:
    return is_search_llm_configured() or is_integration_llm_configured()


# --- Search domains ---
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


def get_active_domains() -> list[str] | None:
    """Return active search domains, or None for unrestricted."""
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
    return list(DEFAULT_SEARCH_DOMAINS.values())


# --- Paths ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- UI ---
APP_TITLE = "AI资讯透视镜 Vision Lens"
APP_ICON = "🔍"
APP_LAYOUT = "wide"
