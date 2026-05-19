"""Vision Lens (AI资讯透视镜) — Streamlit Application Entry Point."""

import streamlit as st

from config import APP_TITLE, APP_ICON, APP_LAYOUT
from ui.styles import apply_theme
from ui.pages.feed import render_feed
from ui.pages.instant import render_instant


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

        from config import LLM_PROVIDER, LLM_MODEL, IS_LLM_CONFIGURED, TAVILY_API_KEY
        provider_names = {"deepseek": "DeepSeek", "anthropic": "Claude", "openai": "OpenAI"}
        provider_display = provider_names.get(LLM_PROVIDER, LLM_PROVIDER)
        model_display = LLM_MODEL.split("/")[-1] if "/" in LLM_MODEL else LLM_MODEL
        llm_status = "✅" if IS_LLM_CONFIGURED else "⚠️ 模拟模式"
        tavily_status = "✅" if TAVILY_API_KEY else "⚠️ 未配置"

        st.markdown(f"""
        <div style="font-size:13px; opacity:0.7; line-height:2;">
            <b>引擎：</b>4-Agent CrewAI 辩论<br>
            <b>模型：</b>{provider_display} / {model_display}<br>
            <b>LLM：</b>{llm_status}<br>
            <b>搜索：</b>{tavily_status}
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


def _render_settings():
    """Render search domain settings trigger in the sidebar."""
    from config import DEFAULT_SEARCH_DOMAINS

    if "search_domains" not in st.session_state:
        st.session_state.search_domains = dict(DEFAULT_SEARCH_DOMAINS)
    if "search_unrestricted" not in st.session_state:
        st.session_state.search_unrestricted = False
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False

    if st.button(
        "⚙️ 搜索设置 ▲" if st.session_state.show_settings else "⚙️ 搜索设置",
        use_container_width=True,
    ):
        st.session_state.show_settings = not st.session_state.show_settings

    if st.session_state.show_settings:
        st.markdown("---")
        st.caption("调整搜索引擎覆盖的网站范围，取消勾选则不搜索该站点。")

        unrestricted = st.checkbox(
            "全量搜索（不限制域名）",
            value=st.session_state.search_unrestricted,
            key="settings_unrestricted",
        )
        st.session_state.search_unrestricted = unrestricted

        if not unrestricted:
            domains = st.session_state.search_domains

            st.caption("中文站点")
            cn_sites = ["知乎", "微博", "搜狐", "新浪", "网易", "腾讯", "澎湃新闻", "凤凰网", "观察者网", "财新"]
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

            st.caption("英文站点")
            en_sites = ["BBC", "CNN", "路透社", "美联社", "纽约时报", "卫报", "华盛顿邮报"]
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

        if st.button("重置为默认", use_container_width=True, key="settings_reset"):
            st.session_state.search_domains = dict(DEFAULT_SEARCH_DOMAINS)
            st.session_state.search_unrestricted = False
            st.rerun()


if __name__ == "__main__":
    main()
