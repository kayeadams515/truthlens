"""Reusable Streamlit UI components for Vision Lens."""

import streamlit as st
import plotly.graph_objects as go


def truth_probability_gauge(probability: float, rationale: str = ""):
    """Render a truth probability gauge using Plotly."""
    bar_color = "#00bfa5" if probability >= 50 else "#dc3545"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability,
        number={"font": {"size": 48, "family": "monospace"}},
        title={"text": "真相可能概率", "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": bar_color},
            "steps": [
                {"range": [0, 30], "color": "rgba(220,53,69,0.12)"},
                {"range": [30, 60], "color": "rgba(240,165,0,0.12)"},
                {"range": [60, 100], "color": "rgba(0,191,165,0.12)"},
            ],
            "threshold": {
                "line": {"color": "#d63384", "width": 3},
                "thickness": 0.75,
                "value": probability,
            },
        },
    ))
    fig.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    if rationale:
        with st.expander("📐 概率计算依据"):
            st.markdown(rationale)


def sentiment_bar_chart(sentiment_stats: dict):
    """Render a horizontal sentiment bar chart."""
    labels = {
        "angry": "愤怒 😡", "fearful": "恐惧 😨", "neutral": "中立 😐",
        "supportive": "支持 👍", "sympathetic": "同情 🤝", "sarcastic": "讽刺 😏",
    }
    items = sorted(sentiment_stats.items(), key=lambda x: x[1], reverse=True)
    display_labels = [labels.get(k, k) for k, v in items]
    values = [v * 100 for k, v in items]
    colors = ["#dc3545", "#fd7e14", "#6c757d", "#00bfa5", "#0d6efd", "#d63384"]

    fig = go.Figure(go.Bar(
        y=display_labels, x=values, orientation="h",
        marker=dict(color=colors[:len(values)]),
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title={"text": "评论区情绪分布", "font": {"size": 16}},
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"showgrid": False, "showticklabels": False, "zeroline": False},
        yaxis={"showgrid": False},
        margin=dict(l=20, r=80, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


def evidence_radar_chart(categories: dict):
    """Render a radar chart for evidence completeness."""
    labels = list(categories.keys())
    values = list(categories.values())

    fig = go.Figure(go.Scatterpolar(
        r=values, theta=labels, fill="toself",
        fillcolor="rgba(0,191,165,0.12)",
        line=dict(color="#00bfa5", width=2),
    ))
    fig.update_layout(
        title={"text": "证据链完整度雷达图", "font": {"size": 16}},
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            radialaxis=dict(range=[0, 100], showticklabels=True, ticks=""),
        ),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


def report_card(topic: str, category: str, truth_prob: float,
                summary: str, source_id: str, source_type: str = "mock"):
    """Render a single report card for the discovery feed.

    Args:
        source_type: "mock" for built-in scenarios, "saved" for persisted reports,
                     "weekly" for auto-searched weekly news.
    """
    prob_color = "#00bfa5" if truth_prob >= 60 else "#f0a500" if truth_prob >= 40 else "#dc3545"

    st.markdown(f"""
    <div class="cyber-card">
        <div style="display:flex; justify-content:space-between; align-items:start; gap:16px;">
            <div style="flex:1; min-width:0;">
                <span class="badge badge-media">{category}</span>
                <h4 class="card-title">{topic}</h4>
                <p style="opacity:0.7; font-size:13px; margin:0;">{summary[:120]}{'...' if len(summary) > 120 else ''}</p>
            </div>
            <div style="text-align:center; min-width:90px; flex-shrink:0;">
                <div class="gauge-big" style="color:{prob_color};">{truth_prob}%</div>
                <div class="gauge-label">真相概率</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn_label = "⚡ 开始透视分析" if source_type == "weekly" else "查看详细报告 →"
    btn_key = f"analyze_{source_type}_{source_id}"

    if st.button(btn_label, key=btn_key, use_container_width=True):
        st.session_state.analyze_topic = topic
        st.session_state.analyze_mode = "controversy"
        st.session_state.current_page = "instant"
        st.rerun()


def agent_thought_block(agent_name: str, agent_type: str, content: str):
    """Render an agent's thought process block."""
    st.markdown(f"""
    <div class="thought-block {agent_type}">
        <strong>[{agent_name}]</strong> 思考中...
        <p style="margin:6px 0 0 0; opacity:0.8;">{content[:200]}...</p>
    </div>
    """, unsafe_allow_html=True)
