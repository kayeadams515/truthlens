"""Discovery Feed page — search + weekly news + history."""

import streamlit as st

from utils.persistence import load_reports
from utils.weekly_news import fetch_weekly_hot_news, get_fallback_weekly_news


def render_feed():
    """Render the discovery feed page with search bar at top."""
    st.markdown("""
    <div style="text-align:center; margin-bottom:24px;">
        <h2>📡 发现·透视报告</h2>
        <p style="opacity:0.6;">搜索新闻 · 本周热点 · 历史报告</p>
    </div>
    """, unsafe_allow_html=True)

    # ========================================
    # Search Bar (moved from instant page)
    # ========================================
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        topic = st.text_input(
            "🔍 输入你想透视的新闻事件",
            placeholder="输入新闻关键词或粘贴链接...",
            label_visibility="collapsed",
            key="feed_search_input",
        )
    with col2:
        mode = st.selectbox(
            "分析模式",
            ["📋 资讯模式", "⚔️ 争议模式"],
            label_visibility="collapsed",
            key="feed_search_mode",
        )
    with col3:
        search_btn = st.button("🔍 开始透视", use_container_width=True, type="primary", key="feed_search_btn")

    is_controversy = "争议" in mode
    if is_controversy:
        st.caption("⚔️ 争议模式：4-Agent 辩论流水线，深度交叉验证各方说辞，计算真相概率。约 30-90 秒。")
    else:
        st.caption("📋 资讯模式：快速搜集和梳理信息，展示事件全貌。")

    if search_btn and topic.strip():
        st.session_state.analyze_topic = topic.strip()
        st.session_state.analyze_mode = "controversy" if is_controversy else "info"
        st.session_state.from_feed = True
        st.session_state.current_page = "instant"
        st.rerun()

    st.divider()

    # ========================================
    # Weekly Hot News
    # ========================================
    if not st.session_state.get("weekly_news_loaded"):
        with st.spinner("🔍 正在搜索本周热点新闻..."):
            try:
                weekly_data = fetch_weekly_hot_news()
            except Exception as e:
                logger.warning(f"Weekly news fetch failed: {e}")
                weekly_data = get_fallback_weekly_news()
            st.session_state.weekly_data = weekly_data
            st.session_state.weekly_news_loaded = True
    else:
        weekly_data = st.session_state.get("weekly_data", {"china": [], "global": []})

    china_news = weekly_data.get("china", [])
    global_news = weekly_data.get("global", [])

    # China news
    col_title, col_btn = st.columns([5, 1])
    with col_title:
        st.markdown("### 🇨🇳 中国热点")
    with col_btn:
        if st.button("🔄 刷新", key="refresh_cn", use_container_width=True):
            st.session_state.weekly_news_loaded = False
            # Also bust the file cache so fetch_weekly_hot_news re-searches
            import os
            cache_file = "data/weekly_news_cache.json"
            if os.path.exists(cache_file):
                os.remove(cache_file)
            st.rerun()
    if china_news:
        _render_news_grid(china_news, "cn")
    else:
        st.caption("暂无数据")
    st.divider()

    # Global news
    st.markdown("### 🌍 全球热点")
    if global_news:
        _render_news_grid(global_news, "global")
    else:
        st.caption("暂无数据")

    # ========================================
    # History
    # ========================================
    saved_reports = load_reports(limit=20)
    if saved_reports:
        st.divider()
        st.markdown("### 📋 历史透视报告")
        for report in saved_reports:
            truth_prob = report.get("truth_probability", 50)
            summary = report.get("summary", "")[:120]
            generated = report.get("generated_at", "")[:10]
            topic_text = report.get("topic", "未知事件")
            prob_color = "#00bfa5" if truth_prob >= 60 else "#f0a500" if truth_prob >= 40 else "#dc3545"

            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="cyber-card" style="padding:14px;">
                    <span class="badge badge-official">已分析 · {generated}</span>
                    <strong>{topic_text}</strong>
                    <p style="opacity:0.6; font-size:13px; margin:4px 0;">{summary}...</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style="text-align:center; padding-top:12px;">
                    <span style="font-size:24px; font-weight:700; color:{prob_color};">{truth_prob}%</span>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                if st.button("📄 查看", key=f"saved_{report['id']}", use_container_width=True):
                    st.session_state.view_report_id = report["id"]
                    st.rerun()

            if st.session_state.get("view_report_id") == report["id"]:
                st.divider()
                st.markdown("---")
                # Render full report with dashboard
                report_content = report.get("markdown_report", "")
                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.markdown(report_content, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Dashboard for history
                st.divider()
                st.markdown("### 📊 数据透视")
                try:
                    from ui.pages.instant import _render_controversy_dashboard, _extract_sentiment
                    _render_controversy_dashboard(report_content, topic_text)
                except Exception:
                    st.caption("图表加载失败")

                if st.button("✕ 收起", key=f"close_{report['id']}"):
                    del st.session_state.view_report_id
                    st.rerun()
                st.divider()



def _extract_location(item: dict) -> str:
    """Extract a location from the news item."""
    content = item.get("content", "")
    title = item.get("title_cn") or item.get("title", "")
    text = title + " " + content
    # Common location patterns
    locations = ["香港", "北京", "上海", "深圳", "广州", "台湾", "美国", "英国", "日本",
                 "韩国", "法国", "德国", "印度", "俄罗斯", "乌克兰", "中东", "欧盟"]
    found = []
    for loc in locations:
        if loc in text and loc not in found:
            found.append(loc)
    return ", ".join(found[:3]) if found else "综合"


def _extract_brief(item: dict) -> str:
    """Extract a one-line event brief."""
    content = item.get("content", "")
    # Clean and truncate
    brief = content.strip()[:80]
    if len(content) > 80:
        brief += "..."
    return brief


def _render_news_grid(news_items: list[dict], prefix: str):
    """Render news cards in grid. Click fills topic + mode and navigates to instant."""
    controversy_badges = {
        "high": '<span class="badge badge-danger">🔥 高争议</span>',
        "medium": '<span class="badge badge-media">📊 中等热度</span>',
        "low": '<span class="badge badge-official">📋 资讯</span>',
    }

    for row_start in range(0, min(len(news_items), 6), 3):
        cols = st.columns(3)
        for col_idx in range(3):
            idx = row_start + col_idx
            if idx >= len(news_items):
                break
            item = news_items[idx]
            with cols[col_idx]:
                try:
                    _render_single_news_card(item, idx, prefix, controversy_badges)
                except Exception as e:
                    st.error(f"渲染卡片失败: {e}")


def _render_single_news_card(item: dict, idx: int, prefix: str, controversy_badges: dict):
    """Render a single news card with expand-to-reveal action buttons."""
    title_cn = item.get("title_cn") or item.get("title", "未知")
    controversy = item.get("controversy", "medium")
    badge_html = controversy_badges.get(controversy, controversy_badges["medium"])
    location = _extract_location(item)
    event_brief = _extract_brief(item)

    st.markdown(f"""
    <div class="cyber-card" style="padding:14px;">
        {badge_html}
        <h4 class="card-title" style="font-size:14px; margin:6px 0;">{title_cn[:60]}</h4>
        <p style="opacity:0.7; font-size:13px; margin:4px 0;">{event_brief}</p>
        <span style="font-size:11px; opacity:0.5;">📍 {location}</span>
    </div>
    """, unsafe_allow_html=True)

    selected_key = f"{prefix}_selected_{idx}"
    if selected_key not in st.session_state:
        st.session_state[selected_key] = False

    if not st.session_state[selected_key]:
        if st.button("🔍 分析此事件", key=f"{prefix}_toggle_{idx}", use_container_width=True):
            st.session_state[selected_key] = True
            st.rerun()
    else:
        if st.button("✕ 收起", key=f"{prefix}_toggle_{idx}", use_container_width=True):
            st.session_state[selected_key] = False
            st.rerun()
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📋 资讯模式", key=f"{prefix}_info_{idx}", use_container_width=True):
                st.session_state.analyze_topic = title_cn
                st.session_state.analyze_mode = "info"
                st.session_state.from_feed = True
                st.session_state.current_page = "instant"
                st.rerun()
        with col_b:
            if st.button("⚔️ 争议模式", key=f"{prefix}_cont_{idx}", use_container_width=True):
                st.session_state.analyze_topic = title_cn
                st.session_state.analyze_mode = "controversy"
                st.session_state.from_feed = True
                st.session_state.current_page = "instant"
                st.rerun()
