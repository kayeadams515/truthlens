"""Vision Lens (AI资讯透视镜) — Streamlit Application Entry Point."""

import json
import os
from pathlib import Path

import streamlit as st

from config import APP_TITLE, APP_ICON, APP_LAYOUT
from ui.styles import apply_theme
from ui.pages.feed import render_feed
from ui.pages.instant import render_instant

SETTINGS_FILE = Path(__file__).parent / "data" / "settings.json"

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
    """Persist current LLM, search provider, and domain settings to disk."""
    payload = {}
    for prefix in ["search_llm", "integration_llm"]:
        payload[prefix] = {
            k: st.session_state.get(f"{prefix}_{k}", "")
            for k in LLM_SETTING_KEYS
        }
    payload["search_provider"] = st.session_state.get("search_provider", "tavily")
    for key in ("tavily_api_key", "brave_api_key", "serpapi_api_key", "searxng_base_url"):
        payload[key] = st.session_state.get(key, "")
    payload["search_domains"] = st.session_state.get("search_domains", {})
    payload["search_unrestricted"] = st.session_state.get("search_unrestricted", False)
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
    if "current_page" not in st.session_state:
        st.session_state.current_page = "feed"
    if "analyze_topic" not in st.session_state:
        st.session_state.analyze_topic = ""
    if "weekly_news_loaded" not in st.session_state:
        st.session_state.weekly_news_loaded = False
    from config import DEFAULT_SEARCH_DOMAINS
    if "search_domains" not in st.session_state:
        st.session_state.search_domains = dict(DEFAULT_SEARCH_DOMAINS)
    if "search_unrestricted" not in st.session_state:
        st.session_state.search_unrestricted = False
    from config import LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, LLM_BASE_URL
    saved = _load_settings()
    for prefix in ["search_llm", "integration_llm"]:
        if f"{prefix}_provider" not in st.session_state:
            saved_cfg = saved.get(prefix, {})
            st.session_state[f"{prefix}_provider"] = saved_cfg.get("provider") or LLM_PROVIDER
            st.session_state[f"{prefix}_model"] = saved_cfg.get("model") or LLM_MODEL
            st.session_state[f"{prefix}_api_key"] = saved_cfg.get("api_key") or LLM_API_KEY
            st.session_state[f"{prefix}_base_url"] = saved_cfg.get("base_url") or LLM_BASE_URL
    # Search provider
    if "search_provider" not in st.session_state:
        st.session_state.search_provider = saved.get("search_provider", "tavily")
    for key in ("tavily_api_key", "brave_api_key", "serpapi_api_key", "searxng_base_url"):
        if key not in st.session_state:
            st.session_state[key] = saved.get(key, "") or os.environ.get(key.upper(), "")

    # ---- Theme ----
    apply_theme()

    # ---- Header ----
    st.markdown("""
    <div style="text-align:center; padding:16px 0 24px 0;">
        <h1 style="font-size:2.4em; margin:0; font-weight:800;">
            <span style="color:#00bfa5;">AI资讯透视镜</span>
        </h1>
        <p style="opacity:0.6; font-size:1em; margin-top:6px;">
            Vision Lens — 穿透信息迷雾，还原事实本相
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ---- Sidebar ----
    with st.sidebar:
        st.markdown("### 📋 导航")
        page_labels = ["🏠 首页", "📄 详情"]
        page_keys = ["feed", "instant"]
        current_idx = page_keys.index(st.session_state.current_page) if st.session_state.current_page in page_keys else 0

        selected_label = st.radio("选择页面", page_labels, index=current_idx, label_visibility="collapsed")
        st.session_state.current_page = page_keys[page_labels.index(selected_label)]

        st.divider()

        from config import is_search_llm_configured, is_integration_llm_configured
        from utils.search_providers import PROVIDERS as SEARCH_PROVIDERS, get_search_provider
        provider_names = {"deepseek": "DeepSeek", "anthropic": "Claude", "openai": "OpenAI"}

        def _model_info(prefix: str) -> str:
            provider = st.session_state.get(f"{prefix}_provider", "deepseek")
            model = st.session_state.get(f"{prefix}_model", "")
            model_short = model.split("/")[-1] if "/" in model else model
            return f"{provider_names.get(provider, provider)} / {model_short}"

        llm1_ok = "✅" if is_search_llm_configured() else "⚠️"
        llm2_ok = "✅" if is_integration_llm_configured() else "⚠️"
        search_provider_key = get_search_provider()
        search_display = SEARCH_PROVIDERS.get(search_provider_key, search_provider_key)

        st.markdown(f"""
        <div style="font-size:13px; opacity:0.7; line-height:2;">
            <b>引擎：</b>4-Agent CrewAI 辩论<br>
            <b>情报 LLM：</b>{_model_info("search_llm")} {llm1_ok}<br>
            <b>分析 LLM：</b>{_model_info("integration_llm")} {llm2_ok}<br>
            <b>搜索：</b>{search_display}
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
    st.markdown("""
    <div style="text-align:center; padding:16px; opacity:0.5; font-size:12px;">
        AI资讯透视镜 Vision Lens v0.3.0 · 4-Agent CrewAI 辩论引擎<br>
        分析结果仅供参考，事实性信息请以官方发布为准
    </div>
    """, unsafe_allow_html=True)

    # ---- Settings (appended to sidebar) ----
    with st.sidebar:
        st.divider()
        _render_settings()


PROVIDER_OPTIONS = ["deepseek", "anthropic", "openai"]
PROVIDER_LABELS = {"deepseek": "DeepSeek", "anthropic": "Claude", "openai": "OpenAI"}


def _render_llm_config_section(prefix: str, label: str):
    """Render provider/model/api_key inputs for one LLM slot."""
    st.caption(f"配置 {label} 使用的 LLM")

    prev_provider = st.session_state.get(f"{prefix}_provider", "deepseek")
    provider_idx = PROVIDER_OPTIONS.index(prev_provider) if prev_provider in PROVIDER_OPTIONS else 0
    provider = st.selectbox(
        "提供商",
        PROVIDER_OPTIONS,
        index=provider_idx,
        format_func=lambda x: PROVIDER_LABELS.get(x, x),
        key=f"settings_{prefix}_provider",
    )
    st.session_state[f"{prefix}_provider"] = provider

    model_val = st.text_input(
        "模型名称",
        value=st.session_state.get(f"{prefix}_model", ""),
        key=f"settings_{prefix}_model",
        placeholder="例如: deepseek-chat 或 claude-sonnet-4-6",
    )
    st.session_state[f"{prefix}_model"] = model_val

    api_key_val = st.text_input(
        "API Key",
        value=st.session_state.get(f"{prefix}_api_key", ""),
        type="password",
        key=f"settings_{prefix}_api_key",
        placeholder="输入 API Key",
    )
    st.session_state[f"{prefix}_api_key"] = api_key_val

    base_url_val = st.text_input(
        "Base URL（可选）",
        value=st.session_state.get(f"{prefix}_base_url", ""),
        key=f"settings_{prefix}_base_url",
        placeholder="留空则使用默认地址",
    )
    st.session_state[f"{prefix}_base_url"] = base_url_val


@st.dialog("⚙️ 设置", width="large")
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
        "🌐 搜索域名", "🔍 情报 LLM", "🧠 分析 LLM",
    ])

    # ---- Tab 1: Search Provider + Domains ----
    with tab_domain:
        # -- Provider selection --
        from utils.search_providers import PROVIDERS as SEARCH_PROVIDERS
        current_provider = st.session_state.get("search_provider", "tavily")
        provider_idx = list(SEARCH_PROVIDERS.keys()).index(current_provider) if current_provider in SEARCH_PROVIDERS else 0
        provider = st.selectbox(
            "搜索引擎",
            list(SEARCH_PROVIDERS.keys()),
            index=provider_idx,
            format_func=lambda x: SEARCH_PROVIDERS.get(x, x),
            key="settings_search_provider",
        )
        st.session_state.search_provider = provider

        # -- Provider-specific config --
        if provider == "tavily":
            api_key = st.text_input(
                "Tavily API Key",
                value=st.session_state.get("tavily_api_key", ""),
                type="password",
                key="settings_tavily_api_key",
                placeholder="tvly-...",
            )
            st.session_state.tavily_api_key = api_key
        elif provider == "brave":
            api_key = st.text_input(
                "Brave Search API Key",
                value=st.session_state.get("brave_api_key", ""),
                type="password",
                key="settings_brave_api_key",
                placeholder="BSA...",
            )
            st.session_state.brave_api_key = api_key
            st.caption("免费 2000 次/月，在 brave.com/search/api 申请")
        elif provider == "serpapi":
            api_key = st.text_input(
                "SerpAPI Key",
                value=st.session_state.get("serpapi_api_key", ""),
                type="password",
                key="settings_serpapi_api_key",
            )
            st.session_state.serpapi_api_key = api_key
        elif provider == "searxng":
            base_url = st.text_input(
                "SearXNG 实例地址",
                value=st.session_state.get("searxng_base_url", ""),
                key="settings_searxng_base_url",
                placeholder="https://searxng.example.com",
            )
            st.session_state.searxng_base_url = base_url
            st.caption("需自行部署 SearXNG 实例")
        elif provider == "duckduckgo":
            st.caption("DuckDuckGo 免费使用，无需 API Key。可能被限速。")

        st.divider()

        # -- Domain filter --
        st.caption("域名过滤（仅 Tavily 和 Brave 支持按域名搜索）")

        unrestricted = st.checkbox(
            "全量搜索（不限制域名）",
            value=st.session_state.search_unrestricted,
            key="settings_unrestricted",
        )
        st.session_state.search_unrestricted = unrestricted

        if not unrestricted:
            domains = st.session_state.search_domains

            col_cn, col_en = st.columns(2)
            cn_sites = ["知乎", "微博", "搜狐", "新浪", "网易", "腾讯", "澎湃新闻", "凤凰网", "观察者网", "财新"]
            en_sites = ["BBC", "CNN", "路透社", "美联社", "纽约时报", "卫报", "华盛顿邮报"]

            with col_cn:
                st.caption("中文站点")
                for name in cn_sites:
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

            with col_en:
                st.caption("英文站点")
                for name in en_sites:
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

            st.caption(f"当前覆盖 {len(domains)} 个站点")

        if st.button("重置搜索域名为默认", use_container_width=True, key="settings_reset_domains"):
            st.session_state.search_domains = dict(DEFAULT_SEARCH_DOMAINS)
            st.session_state.search_unrestricted = False
            st.rerun()

    # ---- Tab 2: Scout LLM ----
    with tab_scout:
        st.caption("情报 LLM 用于情报官 (Scout) Agent 的信息搜集、相关性过滤与话题消歧。")
        _render_llm_config_section("search_llm", "情报")

    # ---- Tab 3: Integration LLM ----
    with tab_integ:
        st.caption("分析 LLM 用于审核员、法官、撰稿人 Agent 以及资讯梳理、追问回答。")
        _render_llm_config_section("integration_llm", "分析")

    # ---- Save ----
    st.divider()
    col_save, col_hint = st.columns([1, 3])
    with col_save:
        if st.button("💾 保存设置", use_container_width=True, type="primary", key="settings_save"):
            _save_settings()
            st.success("设置已保存", icon="✅")
    with col_hint:
        st.caption("设置保存后将持久化，下次启动时自动加载。未保存的改动在刷新后丢失。")


def _render_settings():
    """Render the settings button in the sidebar."""
    if st.button("⚙️ 设置", use_container_width=True):
        _settings_dialog()


if __name__ == "__main__":
    main()
