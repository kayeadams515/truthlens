"""Vision Lens (AI资讯透视镜) — Streamlit Application Entry Point."""

import json
import os
from pathlib import Path

import streamlit as st

from config import APP_TITLE, APP_ICON, APP_LAYOUT
from ui.styles import apply_theme
from ui.pages.feed import render_feed
from ui.pages.instant import render_instant
from utils.i18n import t, init_language
from utils.paths import get_data_dir

SETTINGS_FILE = get_data_dir() / "settings.json"

LLM_SETTING_KEYS = ["provider", "model", "api_key", "base_url"]


def _load_settings() -> dict:
    """Load persisted settings from disk. Returns empty dict if not found."""
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_settings():
    """Persist current LLM, search provider, domain settings, and provider cache to disk."""
    env_keys = st.session_state.get("_env_keys", set())
    payload = {}
    for prefix in ["search_llm", "integration_llm"]:
        payload[prefix] = {
            k: st.session_state.get(f"{prefix}_{k}", "")
            for k in LLM_SETTING_KEYS
        }
        # Don't persist env-var-configured keys to disk
        if f"{prefix}_api_key" in env_keys:
            payload[prefix]["api_key"] = ""
    payload["search_provider"] = st.session_state.get("search_provider", "tavily")
    for key in ("tavily_api_key", "brave_api_key", "serpapi_api_key", "searxng_base_url"):
        payload[key] = st.session_state.get(key, "")
        # Don't persist env-var-configured keys to disk
        if key in env_keys:
            payload[key] = ""
    payload["search_domains"] = st.session_state.get("search_domains", {})
    payload["search_unrestricted"] = st.session_state.get("search_unrestricted", False)
    payload["llm_config_cache"] = st.session_state.get("llm_config_cache", {})
    payload["language"] = st.session_state.get("lang", "zh")
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    """Main entry point for the Vision Lens Streamlit app."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=APP_LAYOUT,
        initial_sidebar_state="expanded",
    )

    # ---- Init session state ----
    init_language()
    if "current_page" not in st.session_state:
        st.session_state.current_page = "feed"
    if "analyze_topic" not in st.session_state:
        st.session_state.analyze_topic = ""
    if "weekly_news_loaded" not in st.session_state:
        st.session_state.weekly_news_loaded = False
    from config import DEFAULT_SEARCH_DOMAINS, is_any_llm_configured
    if "search_domains" not in st.session_state:
        st.session_state.search_domains = dict(DEFAULT_SEARCH_DOMAINS)
    else:
        # Merge in any new domains added since last save
        for k, v in DEFAULT_SEARCH_DOMAINS.items():
            if k not in st.session_state.search_domains:
                st.session_state.search_domains[k] = v
    if "search_unrestricted" not in st.session_state:
        st.session_state.search_unrestricted = False
    # Settings button visibility (toggled by typing "Config" in search bar)
    if "settings_visible" not in st.session_state:
        st.session_state.settings_visible = True
    # Track which API keys come from environment variables (server deployment — prevents viewing)
    if "_env_keys" not in st.session_state:
        st.session_state._env_keys = set()
    saved = _load_settings()
    for prefix in ["search_llm", "integration_llm"]:
        if f"{prefix}_provider" not in st.session_state:
            saved_cfg = saved.get(prefix, {})
            st.session_state[f"{prefix}_provider"] = saved_cfg.get("provider", "deepseek")
            st.session_state[f"{prefix}_model"] = saved_cfg.get("model", "deepseek/deepseek-chat")
            st.session_state[f"{prefix}_api_key"] = saved_cfg.get("api_key", "")
            st.session_state[f"{prefix}_base_url"] = saved_cfg.get("base_url", "https://api.deepseek.com")
        # Environment variable override for API keys (server deployment — not viewable in UI)
        env_key = os.environ.get(f"{prefix.upper()}_API_KEY", "")
        if env_key:
            st.session_state[f"{prefix}_api_key"] = env_key
            st.session_state._env_keys.add(f"{prefix}_api_key")
    # Search provider
    if "search_provider" not in st.session_state:
        st.session_state.search_provider = saved.get("search_provider", "tavily")
    for key in ("tavily_api_key", "brave_api_key", "serpapi_api_key", "searxng_base_url"):
        if key not in st.session_state:
            st.session_state[key] = saved.get(key, "")
        # Environment variable override (server deployment — not viewable in UI)
        env_val = os.environ.get(key.upper(), "")
        if env_val:
            st.session_state[key] = env_val
            st.session_state._env_keys.add(key)
    # Provider config cache: persist per-provider settings so switching back restores keys
    if "llm_config_cache" not in st.session_state:
        st.session_state.llm_config_cache = saved.get("llm_config_cache", {})
    # Test result cache: None = untested, True = ok, str = error message
    if "llm_test_results" not in st.session_state:
        st.session_state.llm_test_results = {
            "search_llm": None, "integration_llm": None, "search": None,
        }

    # ---- First-run: language selection ----
    if "lang" not in st.session_state:
        _language_selection_dialog()
        st.stop()  # Wait for user to pick language before showing anything else

    # ---- First-run onboarding ----
    if "onboarding_skipped" not in st.session_state:
        st.session_state.onboarding_skipped = False
    opened_via_onboarding = st.session_state.pop("_onboarding_go_settings", False)
    if opened_via_onboarding:
        _settings_dialog()
    elif not is_any_llm_configured() and not st.session_state.onboarding_skipped:
        _onboarding_dialog()

    # ---- Theme ----
    apply_theme()

    # ---- Header ----
    st.markdown(f"""
    <div style="text-align:center; padding:16px 0 24px 0;">
        <h1 style="font-size:2.4em; margin:0; font-weight:800;">
            <span style="color:#00bfa5;">{t("AI资讯透视镜")}</span>
        </h1>
        <p style="opacity:0.6; font-size:1em; margin-top:6px;">
            {t("Vision Lens — 穿透信息迷雾，还原事实本相")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ---- Sidebar ----
    with st.sidebar:
        st.markdown(t("### 📋 导航"))
        page_labels = [t("🏠 首页"), t("📄 详情")]
        page_keys = ["feed", "instant"]
        current_idx = page_keys.index(st.session_state.current_page) if st.session_state.current_page in page_keys else 0

        selected_label = st.radio(t("选择页面"), page_labels, index=current_idx, label_visibility="collapsed")
        st.session_state.current_page = page_keys[page_labels.index(selected_label)]

        st.divider()

        from config import is_search_llm_configured, is_integration_llm_configured
        from utils.search_providers import PROVIDERS as SEARCH_PROVIDERS, get_search_provider

        def _model_info(prefix: str) -> str:
            provider = st.session_state.get(f"{prefix}_provider", "deepseek")
            model = st.session_state.get(f"{prefix}_model", "")
            model_short = model.split("/")[-1] if "/" in model else model
            return f"{PROVIDER_LABELS.get(provider, provider)} / {model_short}"

        def _status_icon(prefix: str) -> str:
            result = st.session_state.get("llm_test_results", {}).get(prefix)
            if result is None:
                configured = (is_search_llm_configured() if prefix == "search_llm"
                             else is_integration_llm_configured() if prefix == "integration_llm"
                             else bool(st.session_state.get("search_provider")))
                return "⬜" if configured else "⚠️"
            if result is True:
                return "✅"
            return "❌"

        search_provider_key = get_search_provider()
        search_display = SEARCH_PROVIDERS.get(search_provider_key, search_provider_key)

        st.markdown(f"""
        <div style="font-size:13px; opacity:0.7; line-height:2;">
            <b>{t("情报 LLM：")}</b>{_model_info("search_llm")} {_status_icon("search_llm")}<br>
            <b>{t("分析 LLM：")}</b>{_model_info("integration_llm")} {_status_icon("integration_llm")}<br>
            <b>{t("搜索：")}</b>{search_display} {_status_icon("search")}
        </div>
        """, unsafe_allow_html=True)
        st.divider()

    # ---- Route ----
    if st.session_state.current_page == "feed":
        render_feed()
    else:
        render_instant()

    # ---- Footer ----
    st.divider()
    st.markdown(f"""
    <div style="text-align:center; padding:16px; opacity:0.5; font-size:12px;">
        Vision Lens v0.3.0<br>
        {t("分析结果仅供参考，事实性信息请以官方发布为准")}
    </div>
    """, unsafe_allow_html=True)

    # ---- Settings button (rendered in sidebar, hidden via "Config" toggle) ----
    if st.session_state.get("settings_visible", True):
        with st.sidebar:
            st.divider()
            if st.button(t("⚙️ 设置"), use_container_width=True):
                st.session_state._trigger_settings = True
                st.rerun()

    # ---- Settings dialog (called at top level, NOT inside sidebar) ----
    if st.session_state.pop("_trigger_settings", False):
        _settings_dialog()


PROVIDER_OPTIONS = ["deepseek", "anthropic", "openai", "google", "moonshot", "zhipu", "qwen", "mistral", "xai"]
PROVIDER_LABELS = {
    "deepseek":  "DeepSeek",
    "anthropic": "Claude",
    "openai":    "OpenAI",
    "google":    "Google Gemini",
    "moonshot":  "Moonshot (月之暗面)",
    "zhipu":     "智谱 GLM",
    "qwen":      "通义千问",
    "mistral":   "Mistral AI",
    "xai":       "xAI Grok",
}
PROVIDER_DEFAULTS = {
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
PROVIDER_MODELS = {
    "deepseek": [
        "deepseek/deepseek-chat",
        "deepseek/deepseek-reasoner",
    ],
    "anthropic": [
        "anthropic/claude-sonnet-4-6",
        "anthropic/claude-opus-4-7",
        "anthropic/claude-haiku-4-5-20251001",
        "anthropic/claude-sonnet-4-5",
    ],
    "openai": [
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "openai/gpt-4.1",
        "openai/o3",
        "openai/o4-mini",
    ],
    "google": [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ],
    "moonshot": [
        "moonshot-v1-8k",
        "moonshot-v1-32k",
        "moonshot-v1-128k",
    ],
    "zhipu": [
        "glm-4-plus",
        "glm-4-flash",
        "glm-4",
    ],
    "qwen": [
        "qwen-max",
        "qwen-plus",
        "qwen-turbo",
    ],
    "mistral": [
        "mistral/mistral-large-latest",
        "mistral/mistral-medium-latest",
        "mistral/mistral-small-latest",
    ],
    "xai": [
        "grok-3-beta",
        "grok-2",
    ],
}

CUSTOM_MODEL_TOKEN = "✏️ 自定义模型..."

_KEY_MASK_PLACEHOLDER = "••••••••"

def _mask_api_key(key: str) -> str:
    """Mask an API key for display, keeping only a format hint (last 4 chars)."""
    if not key or len(key) <= 8:
        return _KEY_MASK_PLACEHOLDER
    suffix = key[-4:]
    if key.startswith(("sk-", "tvly-", "BSA")):
        return f"{key[:4]}••••{suffix}"
    return f"••••••{suffix}"


def _test_llm_connection(prefix: str):
    """Test LLM connectivity using CrewAI. Returns (ok: bool, message: str)."""
    model = st.session_state.get(f"{prefix}_model", "")
    api_key = st.session_state.get(f"{prefix}_api_key", "")
    base_url = st.session_state.get(f"{prefix}_base_url", "")
    if not api_key:
        return False, t("未配置 API Key")
    try:
        from crewai import LLM
        kwargs = {"model": model, "api_key": api_key, "temperature": 0.0}
        if base_url:
            kwargs["base_url"] = base_url
        if "/" not in model:
            kwargs["provider"] = "openai"
        llm = LLM(**kwargs)
        resp = llm.call(messages=[{"role": "user", "content": "Say OK"}])
        return (True, t("可用")) if resp else (False, t("返回为空"))
    except Exception as e:
        return False, str(e)[:120]


def _test_search_connection():
    """Test search provider. Returns (ok: bool, message: str)."""
    try:
        from utils.search_providers import search
        results = search(query="test", max_results=1, search_depth="basic", topic="news", days=1)
        if not results:
            return False, t("搜索无结果")
        if results[0].get("error"):
            return False, results[0]["error"][:120]
        return True, t("可用")
    except Exception as e:
        return False, str(e)[:120]


def _render_llm_config_section(prefix: str, label: str):
    """Render provider/model/api_key inputs for one LLM slot."""
    st.caption(t("配置 {label} 使用的 LLM", label=label))

    current_provider = st.session_state.get(f"{prefix}_provider", "deepseek")
    provider_idx = PROVIDER_OPTIONS.index(current_provider) if current_provider in PROVIDER_OPTIONS else 0
    provider = st.selectbox(
        t("提供商"),
        PROVIDER_OPTIONS,
        index=provider_idx,
        format_func=lambda x: PROVIDER_LABELS.get(x, x),
        key=f"settings_{prefix}_provider",
    )

    # When provider changes: cache old config, restore new from cache or use defaults
    if provider != current_provider:
        cache = st.session_state.get("llm_config_cache", {})
        # Save current provider's config to cache
        cache.setdefault(prefix, {})[current_provider] = {
            "model": st.session_state.get(f"{prefix}_model", ""),
            "api_key": st.session_state.get(f"{prefix}_api_key", ""),
            "base_url": st.session_state.get(f"{prefix}_base_url", ""),
        }
        # Restore new provider's config from cache, or use defaults
        cached = cache.get(prefix, {}).get(provider)
        if cached and cached.get("api_key"):
            new_model, new_url, new_key = cached["model"], cached["base_url"], cached["api_key"]
        else:
            defs = PROVIDER_DEFAULTS.get(provider, {})
            new_model, new_url, new_key = defs.get("model", ""), defs.get("base_url", ""), ""
        st.session_state["llm_config_cache"] = cache
        st.session_state[f"{prefix}_provider"] = provider
        st.session_state[f"{prefix}_model"] = new_model
        st.session_state[f"{prefix}_base_url"] = new_url
        st.session_state[f"{prefix}_api_key"] = new_key
        # Reset test result when provider changes
        st.session_state.setdefault("llm_test_results", {})[prefix] = None
        # Explicitly set widget keys so widgets render with new values
        st.session_state[f"settings_{prefix}_model_select"] = new_model
        st.session_state[f"settings_{prefix}_model_custom"] = ""
        st.session_state[f"settings_{prefix}_api_key"] = new_key
        st.session_state[f"settings_{prefix}_base_url"] = new_url

    st.session_state[f"{prefix}_provider"] = provider
    defaults = PROVIDER_DEFAULTS.get(provider, {})
    preset_models = PROVIDER_MODELS.get(provider, [])
    current_model = st.session_state.get(f"{prefix}_model", "")

    # Model: selectbox with presets + custom option
    is_custom = bool(current_model) and current_model not in preset_models
    select_options = preset_models + [CUSTOM_MODEL_TOKEN]
    if is_custom:
        select_idx = len(preset_models)
    elif current_model in preset_models:
        select_idx = preset_models.index(current_model)
    else:
        select_idx = 0

    selected = st.selectbox(
        t("模型"),
        select_options,
        index=select_idx,
        key=f"settings_{prefix}_model_select",
    )

    if selected == CUSTOM_MODEL_TOKEN:
        custom_val = st.text_input(
            t("自定义模型名称"),
            value=current_model if is_custom else "",
            key=f"settings_{prefix}_model_custom",
            placeholder=t("输入模型 ID，如 claude-sonnet-4-6"),
        )
        st.session_state[f"{prefix}_model"] = custom_val
    else:
        st.session_state[f"{prefix}_model"] = selected

    current_api_key = st.session_state.get(f"{prefix}_api_key", "")
    is_env_key = f"{prefix}_api_key" in st.session_state.get("_env_keys", set())

    if is_env_key:
        st.success(t("✓ 已通过环境变量配置（服务器只读）"))
        st.caption(t("如需更换，请联系服务器管理员"))
    elif current_api_key:
        # Already configured — show masked display with change button
        show_change = st.session_state.get(f"_show_change_{prefix}", False)
        if show_change:
            new_key = st.text_input(
                t("新 API Key"),
                type="password",
                key=f"_new_{prefix}_api_key",
                placeholder=t("输入新 API Key..."),
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t("取消"), key=f"_cancel_{prefix}"):
                    st.session_state[f"_show_change_{prefix}"] = False
                    st.rerun()
            with col2:
                if st.button(t("确认更换 Key"), key=f"_confirm_{prefix}"):
                    if new_key:
                        st.session_state[f"{prefix}_api_key"] = new_key
                    st.session_state[f"_show_change_{prefix}"] = False
                    st.rerun()
        else:
            st.text_input(
                t("API Key"),
                value=_mask_api_key(current_api_key),
                disabled=True,
                key=f"_masked_{prefix}_api_key",
            )
            if st.button(t("🔄 更换 API Key"), key=f"_change_btn_{prefix}"):
                st.session_state[f"_show_change_{prefix}"] = True
                st.rerun()
    else:
        # Not configured — show empty input
        api_key_val = st.text_input(
            t("API Key"),
            type="password",
            key=f"settings_{prefix}_api_key",
            placeholder=t("输入 API Key"),
        )
        if api_key_val:
            st.session_state[f"{prefix}_api_key"] = api_key_val

    base_url_val = st.text_input(
        t("Base URL（可选）"),
        value=st.session_state.get(f"{prefix}_base_url", ""),
        key=f"settings_{prefix}_base_url",
        placeholder=defaults.get("base_url", t("留空则使用默认地址")),
    )
    st.session_state[f"{prefix}_base_url"] = base_url_val


def _render_search_api_key(session_key: str, label: str, placeholder: str):
    """Render a search provider API key input with masking after configuration."""
    current_key = st.session_state.get(session_key, "")
    is_env_key = session_key in st.session_state.get("_env_keys", set())

    if is_env_key:
        st.success(t("✓ {label} — 已通过环境变量配置（服务器只读）", label=label))
        st.caption(t("如需更换，请联系服务器管理员"))
    elif current_key:
        show_change = st.session_state.get(f"_show_change_{session_key}", False)
        if show_change:
            new_key = st.text_input(
                t("新 {label}", label=label),
                type="password",
                key=f"_new_{session_key}",
                placeholder=t("输入新 Key..."),
            )
            col_c, col_cf = st.columns(2)
            with col_c:
                if st.button(t("取消"), key=f"_cancel_{session_key}"):
                    st.session_state[f"_show_change_{session_key}"] = False
                    st.rerun()
            with col_cf:
                if st.button(t("确认更换 Key"), key=f"_confirm_{session_key}"):
                    if new_key:
                        st.session_state[session_key] = new_key
                    st.session_state[f"_show_change_{session_key}"] = False
                    st.rerun()
        else:
            st.text_input(
                label,
                value=_mask_api_key(current_key),
                disabled=True,
                key=f"_masked_{session_key}",
            )
            if st.button(t("🔄 更换"), key=f"_change_{session_key}"):
                st.session_state[f"_show_change_{session_key}"] = True
                st.rerun()
    else:
        val = st.text_input(
            label,
            type="password",
            key=f"settings_{session_key}",
            placeholder=placeholder,
        )
        if val:
            st.session_state[session_key] = val


@st.dialog(t("⚙️ 设置"), width="large")
def _settings_dialog():
    """Modal dialog for all app settings: domains, search LLM, integration LLM."""
    from config import DEFAULT_SEARCH_DOMAINS

    # Constrain dialog height — target the dialog's own scrollable viewport
    st.markdown("""
    <style>
    [data-testid="stDialog"] > div > div > div {
        max-height: 72vh;
        overflow-y: auto !important;
        overscroll-behavior: contain;
    }
    </style>
    """, unsafe_allow_html=True)

    tab_domain, tab_scout, tab_integ = st.tabs([
        t("🌐 搜索域名"), t("🔍 情报 LLM"), t("🧠 分析 LLM"),
    ])

    # ---- Tab 1: Search Provider + Domains ----
    with tab_domain:
        # -- Provider selection --
        from utils.search_providers import PROVIDERS as SEARCH_PROVIDERS
        current_provider = st.session_state.get("search_provider", "tavily")
        provider_idx = list(SEARCH_PROVIDERS.keys()).index(current_provider) if current_provider in SEARCH_PROVIDERS else 0
        provider = st.selectbox(
            t("搜索引擎"),
            list(SEARCH_PROVIDERS.keys()),
            index=provider_idx,
            format_func=lambda x: SEARCH_PROVIDERS.get(x, x),
            key="settings_search_provider",
        )
        st.session_state.search_provider = provider

        # -- Provider-specific config --
        if provider == "tavily":
            _render_search_api_key("tavily_api_key", "Tavily API Key", "tvly-...")
        elif provider == "brave":
            _render_search_api_key("brave_api_key", "Brave Search API Key", "BSA...")
            st.caption(t("免费 2000 次/月，在 brave.com/search/api 申请"))
        elif provider == "serpapi":
            _render_search_api_key("serpapi_api_key", "SerpAPI Key", "")
        elif provider == "searxng":
            base_url = st.text_input(
                t("SearXNG 实例地址"),
                value=st.session_state.get("searxng_base_url", ""),
                key="settings_searxng_base_url",
                placeholder="https://searxng.example.com",
            )
            st.session_state.searxng_base_url = base_url
            st.caption(t("需自行部署 SearXNG 实例"))
        st.divider()

        # -- Domain filter --
        st.caption(t("域名过滤（Tavily / Brave / SerpAPI 支持按域名搜索，SearXNG 不支持）"))

        unrestricted = st.checkbox(
            t("全量搜索（不限制域名）"),
            value=st.session_state.search_unrestricted,
            key="settings_unrestricted",
        )
        st.session_state.search_unrestricted = unrestricted

        if not unrestricted:
            domains = st.session_state.search_domains

            cn_official = ["新华社", "人民日报", "央视网", "环球时报", "中国新闻网", "光明网"]
            cn_portal  = ["知乎", "微博", "搜狐", "新浪", "网易", "腾讯", "澎湃新闻", "凤凰网", "观察者网", "财新"]
            cn_social  = ["抖音", "小红书"]
            en_media   = ["BBC", "CNN", "路透社", "美联社", "纽约时报", "卫报", "华盛顿邮报"]
            en_social  = ["YouTube", "X(Twitter)", "Facebook", "Instagram", "Reddit", "TikTok"]

            def _render_site_checkboxes(names: list[str]):
                for name in names:
                    domain = domains.get(name, "")
                    checked = st.checkbox(
                        f"{name}  ({domain})",
                        value=(name in domains),
                        key=f"settings_domain_{name}",
                    )
                    if not checked and name in domains:
                        del domains[name]
                    elif checked and name not in domains:
                        domains[name] = DEFAULT_SEARCH_DOMAINS[name]

            col_cn, col_en = st.columns(2)
            with col_cn:
                st.caption(t("🇨🇳 官方媒体"))
                _render_site_checkboxes(cn_official)
                st.caption(t("🇨🇳 门户资讯"))
                _render_site_checkboxes(cn_portal)
                st.caption(t("🇨🇳 社交平台"))
                _render_site_checkboxes(cn_social)
            with col_en:
                st.caption(t("🌍 国际媒体"))
                _render_site_checkboxes(en_media)
                st.caption(t("🌍 社交平台"))
                _render_site_checkboxes(en_social)

            st.caption(t("当前覆盖 {count} 个站点", count=len(domains)))

        if st.button(t("重置搜索域名为默认"), use_container_width=True, key="settings_reset_domains"):
            st.session_state.search_domains = dict(DEFAULT_SEARCH_DOMAINS)
            st.session_state.search_unrestricted = False
            st.rerun()

        st.divider()
        col_st, col_ss = st.columns([1, 2])
        with col_st:
            if st.button(t("🧪 测试搜索"), key="test_search", use_container_width=True):
                with st.spinner(t("正在测试搜索连接...")):
                    ok, msg = _test_search_connection()
                    st.session_state.llm_test_results["search"] = True if ok else msg
        with col_ss:
            _show_test_result("search")

    # ---- Tab 2: Scout LLM ----
    with tab_scout:
        st.caption(t("情报 LLM 用于情报官 (Scout) Agent 的信息搜集、相关性过滤与话题消歧。"))
        _render_llm_config_section("search_llm", t("情报"))
        st.divider()
        col_test1, col_status1 = st.columns([1, 2])
        with col_test1:
            if st.button(t("🧪 测试连接"), key="test_search_llm", use_container_width=True):
                with st.spinner(t("正在测试情报 LLM 连接...")):
                    ok, msg = _test_llm_connection("search_llm")
                    st.session_state.llm_test_results["search_llm"] = True if ok else msg
        with col_status1:
            _show_test_result("search_llm")

    # ---- Tab 3: Integration LLM ----
    with tab_integ:
        st.caption(t("分析 LLM 用于审核员、法官、撰稿人 Agent 以及资讯梳理、追问回答。"))
        _render_llm_config_section("integration_llm", t("分析"))
        st.divider()
        col_test2, col_status2 = st.columns([1, 2])
        with col_test2:
            if st.button(t("🧪 测试连接"), key="test_integration_llm", use_container_width=True):
                with st.spinner(t("正在测试分析 LLM 连接...")):
                    ok, msg = _test_llm_connection("integration_llm")
                    st.session_state.llm_test_results["integration_llm"] = True if ok else msg
        with col_status2:
            _show_test_result("integration_llm")

    # ---- Language Selector ----
    st.divider()
    lang_options = ["中文", "中文（Beta）", "English"]
    lang_code_map = {"中文": "zh", "中文（Beta）": "zh-beta", "English": "en"}
    current_lang = st.session_state.get("lang", "zh")
    current_lang_idx = 0
    for i, label in enumerate(lang_options):
        if lang_code_map[label] == current_lang:
            current_lang_idx = i
            break
    col_lang_label, col_lang_sel = st.columns([1, 2])
    with col_lang_label:
        st.caption(t("语言 / Language"))
    with col_lang_sel:
        selected_lang = st.selectbox(
            t("语言 / Language"),
            lang_options,
            index=current_lang_idx,
            key="settings_lang_selector",
            label_visibility="collapsed",
        )
        new_lang = lang_code_map[selected_lang]
        if new_lang != st.session_state.get("lang", "zh"):
            st.session_state.lang = new_lang
            st.rerun()

    # ---- Save + Test All ----
    st.divider()
    col_test_all, col_save, col_hint = st.columns([1, 1, 3])
    with col_test_all:
        if st.button(t("🧪 测试全部"), key="test_all", use_container_width=True):
            with st.spinner(t("正在测试全部连接...")):
                for pfx in ("search_llm", "integration_llm"):
                    ok, msg = _test_llm_connection(pfx)
                    st.session_state.llm_test_results[pfx] = True if ok else msg
                ok_s, msg_s = _test_search_connection()
                st.session_state.llm_test_results["search"] = True if ok_s else msg_s
    with col_save:
        if st.button(t("💾 保存设置"), use_container_width=True, type="primary", key="settings_save"):
            _save_settings()
            st.success(t("设置已保存"), icon="✅")
    with col_hint:
        st.caption(t("切换厂商时自动缓存已配置的 API Key / URL，切回无需重输。"))


def _show_test_result(key: str):
    """Display a compact test result indicator."""
    result = st.session_state.get("llm_test_results", {}).get(key)
    if result is None:
        st.caption(t("⬜ 未测试"))
    elif result is True:
        st.success(t("✅ 连接可用"))
    else:
        st.error(f"❌ {result}")


@st.dialog("🌐 Language / 语言", width="small")
def _language_selection_dialog():
    """First-run language selection shown before anything else."""
    st.markdown("""
    <div style="text-align:center; padding:10px 0;">
        <h3 style="margin:0;">🌐 Choose your language</h3>
        <p style="opacity:0.5; margin:6px 0 20px;">请选择界面语言</p>
    </div>
    """, unsafe_allow_html=True)
    col_zh, col_zhbeta, col_en = st.columns(3)
    with col_zh:
        if st.button("中文", use_container_width=True, type="primary"):
            st.session_state.lang = "zh"
            st.rerun()
    with col_zhbeta:
        if st.button("中文（Beta）", use_container_width=True):
            st.session_state.lang = "zh-beta"
            st.rerun()
    with col_en:
        if st.button("English", use_container_width=True):
            st.session_state.lang = "en"
            st.rerun()


@st.dialog(t("👋 欢迎使用 AI资讯透视镜"), width="large")
def _onboarding_dialog():
    """First-run dialog guiding user to configure LLM."""
    st.markdown(t("### 🎉 欢迎！开始之前请先配置 AI 模型\n\n"
    "本工具使用 **4-Agent CrewAI 辩论引擎** 进行深度资讯分析，需要至少配置一个 LLM 才能工作。\n\n"
    "**快速开始：**\n"
    "1. 点击下方按钮打开设置\n"
    "2. 在 **🔍 情报 LLM** 标签页选择厂商，填入 API Key\n"
    "3. 点击 **💾 保存设置**\n"
    "4. 点 **🧪 测试连接** 验证可用性\n\n"
    "> 💡 **推荐**：DeepSeek 便宜且中文能力强；Brave Search 提供每月 2000 次免费搜索额度。\n"
    "> 所有配置保存在本地 `data/settings.json`，不会上传。"))
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("⚙️ 打开设置"), use_container_width=True, type="primary"):
            st.session_state._onboarding_go_settings = True
            st.rerun()
    with col2:
        if st.button(t("🔍 先看看（模拟演示）"), use_container_width=True):
            st.session_state.onboarding_skipped = True
            st.rerun()



if __name__ == "__main__":
    main()
