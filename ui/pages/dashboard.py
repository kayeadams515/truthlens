"""Data Dashboard page — charts and statistics for truth analysis."""

import streamlit as st

from tools.mock_data import get_mock_news, list_scenarios
from ui.components import (
    truth_probability_gauge,
    sentiment_bar_chart,
    evidence_radar_chart,
)


def render_dashboard():
    """Render the data dashboard page."""
    st.markdown("""
    <div style="text-align:center; margin-bottom:24px;">
        <h2>📊 数据看板</h2>
        <p style="opacity:0.6;">多维度数据可视化 · 真相概率仪表盘 · 舆情情绪分布</p>
    </div>
    """, unsafe_allow_html=True)

    # Scenario selector
    scenarios = list_scenarios()
    scenario_options = {s["title"][:40]: s["id"] for s in scenarios}
    selected_title = st.selectbox(
        "选择要查看的事件",
        list(scenario_options.keys()),
        label_visibility="collapsed",
    )
    scenario_id = scenario_options[selected_title]

    data = get_mock_news(scenario_id)
    if not data:
        st.warning("数据加载失败")
        return

    # ---- Row 1: Key Metrics ----
    st.markdown("### 📈 核心指标")
    sentiment = data["social_media"]["sentiment_stats"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        truth_prob = _get_truth_prob(scenario_id)
        st.metric("真相可能概率", f"{truth_prob}%", delta=None)
    with col2:
        evidence_score = _get_evidence_score(scenario_id)
        st.metric("证据链完整度", f"{evidence_score}/100")
    with col3:
        dominant = max(sentiment, key=sentiment.get)
        st.metric("主导情绪", _emotion_label(dominant))
    with col4:
        source_count = (
            len(data["official"]["statements"])
            + len(data["we_media"])
            + len(data["social_media"]["representative_comments"])
        )
        st.metric("信息源总数", source_count)

    st.divider()

    # ---- Row 2: Truth Gauge + Sentiment Chart ----
    col_left, col_right = st.columns(2)

    with col_left:
        truth_prob = _get_truth_prob(scenario_id)
        truth_probability_gauge(
            probability=truth_prob,
            rationale=_truth_rationale(scenario_id),
        )

    with col_right:
        sentiment_bar_chart(sentiment)

    st.divider()

    # ---- Row 3: Evidence Radar + Source Reliability ----
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        evidence_categories = _get_evidence_categories(scenario_id)
        evidence_radar_chart(evidence_categories)

    with col_right2:
        st.markdown("### 🎯 来源可靠性评级")
        reliability_data = _get_reliability_data(data)
        for item in reliability_data:
            color = (
                "#00bfa5" if item["score"] >= 0.8
                else "#f0a500" if item["score"] >= 0.6
                else "#dc3545"
            )
            st.markdown(f"""
            <div style="display:flex; align-items:center; margin:12px 0; gap:12px;">
                <div style="flex:1;">
                    <span style="font-size:14px;">{item['source']}</span>
                    <span style="opacity:0.6; font-size:12px; margin-left:8px;">{item['type']}</span>
                </div>
                <div style="width:120px; height:6px; border-radius:3px; background:rgba(128,128,128,0.15);">
                    <div style="width:{item['score']*100}%; background:{color}; height:100%; border-radius:3px;"></div>
                </div>
                <span style="color:{color}; font-size:13px; font-family:monospace; min-width:45px; text-align:right;">
                    {item['score']*100:.0f}%
                </span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ---- Row 4: Key Findings Summary ----
    st.markdown("### 🔑 关键发现")
    findings = _get_key_findings(scenario_id)

    cols = st.columns(len(findings))
    for i, finding in enumerate(findings):
        with cols[i]:
            st.markdown(f"""
            <div class="cyber-card" style="text-align:center;">
                <div style="font-size:2em;">{finding['icon']}</div>
                <h4>{finding['title']}</h4>
                <p style="opacity:0.6; font-size:12px;">{finding['detail']}</p>
            </div>
            """, unsafe_allow_html=True)


# ---- Helpers ----

def _get_truth_prob(scenario_id: str) -> float:
    probs = {"ev_crash": 67.0, "donation": 52.0, "ai_fake": 89.0}
    return probs.get(scenario_id, 50.0)


def _get_evidence_score(scenario_id: str) -> int:
    scores = {"ev_crash": 58, "donation": 71, "ai_fake": 85}
    return scores.get(scenario_id, 50)


def _emotion_label(emotion: str) -> str:
    labels = {
        "angry": "愤怒 😡",
        "fearful": "恐惧 😨",
        "neutral": "中立 😐",
        "supportive": "支持 👍",
        "sympathetic": "同情 🤝",
        "sarcastic": "讽刺 😏",
    }
    return labels.get(emotion, emotion)


def _truth_rationale(scenario_id: str) -> str:
    rationales = {
        "ev_crash": (
            "**先验概率 P(H)**: 60%（新能源车碰撞起火事故中，电池热失控为主要原因的比例）\n\n"
            "**关键证据似然比**:\n"
            "- 行车记录仪视频 (+15%): 直接证据，碰撞→起火时间线清晰\n"
            "- 官方初步调查 (+10%): 权威来源，但尚未完成完整检测\n"
            "- 品牌历史NHTSA调查 (-8%): 增加电池设计缺陷的先验概率\n"
            "- 门把手故障的网友投稿 (-5%): 间接证据，样本可能有偏差\n\n"
            "**后验概率 P(H|E)**: 67%\n"
            "概率打折原因：缺少第三方电池检测报告和车门锁止机构独立鉴定。"
        ),
        "donation": (
            "**先验概率 P(H)**: 40%（网络筹款争议中，存在信息隐瞒但未必构成故意欺诈的比例）\n\n"
            "**关键证据似然比**:\n"
            "- 医院诊断证明 (+20%): 疾病真实存在，排除骗捐\n"
            "- 房产交易记录 (+15%): 证实部分房产已变卖用于治疗\n"
            "- 筹款申报与实际的偏差 (-18%): 未及时更新资产信息\n"
            "- 丈夫企业互助金 (-5%): 有替代资金来源但未披露\n\n"
            "**后验概率 P(H|E)**: 52%\n"
            "概率接近50%反映'信息披露不全但不构成恶意欺诈'的中间状态。"
        ),
        "ai_fake": (
            "**先验概率 P(H)**: 95%（政府公告造假被查实的概率极高）\n\n"
            "**关键证据似然比**:\n"
            "- 技术鉴定报告 (+25%): AI生成特征的明确证据\n"
            "- 警方立案 (+20%): 执法机关确认违法\n"
            "- 中介群传播路径 (+5%): 证实有组织的传播行为\n\n"
            "**后验概率 P(H|E)**: 89%\n"
            "之所以不是100%，是因为造谣者身份和具体动机仍在侦查中。"
        ),
    }
    return rationales.get(scenario_id, "暂无详细概率计算依据。")


def _get_evidence_categories(scenario_id: str) -> dict:
    categories = {
        "ev_crash": {
            "官方通报": 70,
            "行车记录": 85,
            "第三方检测": 20,
            "目击证词": 45,
            "社交媒体": 30,
        },
        "donation": {
            "医院诊断": 90,
            "资产信息": 65,
            "平台审核": 40,
            "媒体报道": 75,
            "公众舆论": 30,
        },
        "ai_fake": {
            "技术鉴定": 95,
            "公安侦查": 70,
            "传播溯源": 60,
            "中介调查": 50,
            "公众认知": 35,
        },
    }
    return categories.get(scenario_id, {})


def _get_reliability_data(data: dict) -> list[dict]:
    results = []
    official = data.get("official", {})
    results.append({
        "source": official.get("source", "官方来源"),
        "type": "官方",
        "score": 0.92,
    })
    for article in data.get("we_media", []):
        interest = article.get("possible_interest", "")
        if "利益相关" in interest or "流量" in interest:
            score = 0.4
        elif "公信力较高" in interest or "独立" in interest:
            score = 0.75
        else:
            score = 0.55
        results.append({
            "source": article["source"],
            "type": "自媒体",
            "score": score,
        })
    results.append({
        "source": "社交媒体(综合)",
        "type": "公众",
        "score": 0.35,
    })
    return results


def _get_key_findings(scenario_id: str) -> list[dict]:
    findings = {
        "ev_crash": [
            {"icon": "🔋", "title": "核心争议", "detail": "电池热失控 vs 碰撞极端工况——国家标准适用性存疑"},
            {"icon": "🚪", "title": "安全缺陷", "detail": "电子门锁断电后无法机械开启——可能构成产品缺陷"},
            {"icon": "📋", "title": "缺失证据", "detail": "第三方电池检测报告 + 车门锁止机构独立鉴定"},
        ],
        "donation": [
            {"icon": "🏥", "title": "核心事实", "detail": "女童患白血病属实，医疗费用真实存在"},
            {"icon": "🏠", "title": "关键争议", "detail": "3套房产中2套已变卖治疗，但未及时更新申报信息"},
            {"icon": "⚖️", "title": "法律边界", "detail": "信息披露不全 ≠ 恶意欺诈，需平台规则厘清"},
        ],
        "ai_fake": [
            {"icon": "🤖", "title": "伪造手段", "detail": "AI生成的公章和公文格式足以以假乱真"},
            {"icon": "💼", "title": "利益驱动", "detail": "房产中介为炒高房价而传播伪造文件"},
            {"icon": "🛡️", "title": "防范建议", "detail": "AI内容强制标注 + 公文在线验证系统"},
        ],
    }
    return findings.get(scenario_id, [])
