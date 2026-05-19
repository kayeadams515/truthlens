"""Central configuration for Vision Lens."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM Provider ---
# Supported: "anthropic", "deepseek", "openai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek").lower()

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# OpenAI-compatible (generic)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# --- LLM Configuration (derived) ---
if LLM_PROVIDER == "deepseek":
    LLM_MODEL = os.getenv("LLM_MODEL", f"deepseek/{DEEPSEEK_MODEL}")
    LLM_API_KEY = DEEPSEEK_API_KEY
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
elif LLM_PROVIDER == "openai":
    LLM_MODEL = os.getenv("LLM_MODEL", f"openai/{OPENAI_MODEL}")
    LLM_API_KEY = OPENAI_API_KEY
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
else:  # anthropic
    LLM_MODEL = os.getenv("LLM_MODEL", f"anthropic/claude-sonnet-4-6")
    LLM_API_KEY = ANTHROPIC_API_KEY
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")

IS_LLM_CONFIGURED = bool(LLM_API_KEY)


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
