"""Detail page — shows analysis results. Receives topic + mode from feed page."""

import streamlit as st
from datetime import datetime

from config import is_any_llm_configured
from utils.logger import logger
from utils.i18n import t


def render_instant():
    """Render the detail/analysis page. Auto-runs if topic is passed in."""
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:24px;">
        <h2>{t("⚡ 透视分析")}</h2>
    </div>
    """, unsafe_allow_html=True)

    if not is_any_llm_configured():
        st.warning(t("⚠️ 未配置 LLM API Key，请在设置中配置后使用。搜索功能可独立使用。"))

    # Get topic and mode from session state
    has_incoming_topic = "analyze_topic" in st.session_state
    has_incoming_mode = "analyze_mode" in st.session_state
    incoming_topic = st.session_state.pop("analyze_topic", "")
    incoming_mode = st.session_state.pop("analyze_mode", "info")
    incoming_controversy_angle = st.session_state.pop("controversy_angle", "")
    incoming_insight_guidance = st.session_state.pop("insight_guidance", "")

    if incoming_topic:
        # New analysis requested — store in persistent key, clear old cache
        st.session_state.current_topic = incoming_topic
        st.session_state.current_mode = incoming_mode
        st.session_state.pop("current_report", None)
        st.session_state.pop("current_summary", None)
        st.session_state.pop("current_search_results", None)
        st.session_state.pop("current_insight_report", None)
        st.session_state.pop("current_insight_data", None)
        st.session_state.pop("qa_history", None)
        st.session_state.pop("current_controversy_angle", None)
        st.session_state.pop("current_intent", None)
    elif has_incoming_mode and incoming_mode != st.session_state.get("current_mode", "info"):
        # Mode switch on same topic (e.g., info → controversy via angle input)
        st.session_state.current_mode = incoming_mode
        st.session_state.pop("current_report", None)  # Clear old controversy report
        if incoming_controversy_angle:
            st.session_state.current_controversy_angle = incoming_controversy_angle

    topic = st.session_state.get("current_topic", "")
    mode = st.session_state.get("current_mode", "info")
    is_controversy = (mode == "controversy")
    is_insight = (mode == "insight")
    controversy_angle = st.session_state.get("current_controversy_angle", "")

    if not topic:
        st.markdown(f"""
        <div style="text-align:center; padding:60px 20px; opacity:0.5;">
            <div style="font-size:64px; margin-bottom:20px;">🔍</div>
            <p style="font-size:18px;">{t("从首页搜索或选择一条新闻开始分析")}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(t("← 返回首页"), use_container_width=True):
            st.session_state.current_page = "feed"
            st.rerun()
        return

    # If report already cached, just redisplay (happens on Q&A rerun)
    cached_report = st.session_state.get("current_report")
    cached_summary = st.session_state.get("current_summary")
    cached_search = st.session_state.get("current_search_results")
    cached_insight_report = st.session_state.get("current_insight_report")
    cached_insight_data = st.session_state.get("current_insight_data")

    if cached_report and is_controversy:
        cached_intent = st.session_state.get("current_intent", "debate_understanding")
        _display_controversy_report(topic, cached_report)
        _render_controversy_dashboard(cached_report, topic, cached_intent)
        _render_followup_qa(topic, cached_report, mode="controversy")
    elif cached_insight_report and is_insight:
        _display_insight_result(topic, cached_insight_report, cached_insight_data)
    elif cached_summary and not is_controversy and not is_insight:
        _display_info_result(topic, cached_summary, cached_search or [])
    elif is_controversy:
        _run_controversy_mode(topic, controversy_angle, cached_search or [])
    elif is_insight:
        _run_insight_mode(topic, incoming_insight_guidance)
    else:
        # Fresh info analysis — disambiguate first if needed
        with st.spinner(t("🔍 正在分析关键词...")):
            resolved_topic = _disambiguate_topic(topic)
        if resolved_topic is None:
            return
        _run_info_mode(resolved_topic)

    # Back button
    st.divider()
    if st.button(t("← 返回首页搜索新事件"), use_container_width=True):
        st.session_state.pop("current_topic", None)
        st.session_state.pop("current_mode", None)
        st.session_state.current_page = "feed"
        st.rerun()


# ============================================================
# Controversy Mode
# ============================================================

def _run_controversy_mode(topic: str, controversy_angle: str = "", info_search_results: list = None):
    if info_search_results is None:
        info_search_results = []

    # Build existing info summary from info mode results
    existing_info = ""
    if info_search_results:
        existing_info = "\n".join(
            f"- {r.get('title', '')} | {r.get('source', '')}\n  {r.get('content', '')[:200]}"
            for r in info_search_results[:8]
        )

    # ---- Classify user intent ----
    intent = "debate_understanding"  # default
    if controversy_angle and is_any_llm_configured():
        intent = _classify_intent(topic, controversy_angle)
    elif not controversy_angle:
        intent = "debate_understanding"

    is_truth_seeking = (intent == "truth_seeking")

    st.markdown(f"""
    <div style="border:1px solid rgba(128,128,128,0.15); border-radius:8px; padding:16px; margin-bottom:20px;">
        <strong>{t("⚔️ 争议分析：")}</strong>{topic}
    </div>
    """, unsafe_allow_html=True)

    if controversy_angle:
        st.markdown(f"""
        <div style="background:rgba(0,191,165,0.08); border-left:3px solid #00bfa5; border-radius:4px; padding:12px; margin-bottom:16px;">
            <small style="opacity:0.7;">{t("🎯 剖析争议点：")}</small><br>
            <strong>{controversy_angle}</strong>
        </div>
        """, unsafe_allow_html=True)

    # Intent badge
    intent_label = t("🔎 争议剖析 — 真相核查") if is_truth_seeking else t("🎭 争议剖析 — 了解争议格局")
    st.caption(f"{intent_label} · {t(intent)}")

    if not is_any_llm_configured():
        st.error(t("⚠️ 未配置 LLM API Key，无法运行争议分析。请在设置中配置 API Key。"))
        return

    # Detailed status display — adapt messages based on intent
    agent_count = "4" if is_truth_seeking else "3"
    status_label = t("⚔️ {agent_count}-Agent 辩论流水线启动中...", agent_count=agent_count)
    if "{agent_count}" not in status_label:
        status_label = f"⚔️ {'4' if is_truth_seeking else '3'}-Agent Pipeline starting..."
    with st.status(status_label, expanded=True) as status:
        st.write(t("🔍 **情报官 (Scout)** — 正在从多源搜索中英文互联网信息..."))
        eta = t("⏳ 预计耗时 20-60 秒，请耐心等待") if not is_truth_seeking else t("⏳ 预计耗时 30-90 秒，请耐心等待")
        st.write(eta)

        start_time = datetime.now()
        report = _run_live_analysis(topic, controversy_angle, existing_info, intent)
        elapsed = (datetime.now() - start_time).total_seconds()

        if report is None:
            status.update(label=t("❌ 分析失败"), state="error")
            return

        status.update(
            label=t("✅ {agent_count}-Agent 辩论完成（耗时 {elapsed:.0f} 秒", agent_count=agent_count, elapsed=elapsed),
            state="complete",
            expanded=False,
        )
        st.write(t("🔍 **情报官** — 完成多源信息搜集"))
        st.write(t("🧐 **审核员** — 完成交叉审查与利益关联分析"))
        if is_truth_seeking:
            st.write(t("⚖️ **法官** — 完成贝叶斯真相概率计算"))
        st.write(t("✍️ **撰稿人** — 完成结构化报告生成"))

    # Cache for redisplay on Q&A rerun
    st.session_state.current_report = report
    st.session_state.current_intent = intent
    _save_report(topic, report)

    _display_controversy_report(topic, report)
    _render_controversy_dashboard(report, topic, intent)
    _render_followup_qa(topic, report, mode="controversy")


def _classify_intent(topic: str, angle: str) -> str:
    """Classify user intent as debate_understanding or truth_seeking."""
    try:
        from config import create_search_llm
        llm = create_search_llm(temperature=0.0)
        result = llm.call(messages=[{"role": "user", "content": t(
            "prompt.classify_intent", topic=topic, angle=angle
        )}])
        result = result.strip()
        if result.startswith("```"):
            lines = result.split("\n")
            result = "\n".join(lines[1:]) if len(lines) > 1 else result
            if result.endswith("```"):
                result = result[:-3]
        import json
        data = json.loads(result)
        intent = data.get("intent", "debate_understanding")
        logger.info(f"Intent classified: {intent} ({data.get('reason', '')})")
        return intent if intent in ("debate_understanding", "truth_seeking") else "debate_understanding"
    except Exception:
        return "debate_understanding"


# ============================================================
# Insight Mode
# ============================================================

def _run_insight_mode(topic: str, guidance: str = ""):
    """Adaptive insight analysis — social-media-focused, topic-type-aware.
    2-step direct LLM: topic-type analysis → narrative synthesis.
    No CrewAI involved — faster and more creative than controversy mode.
    """
    st.markdown(f"""
    <div style="border:1px solid rgba(128,128,128,0.15); border-radius:8px; padding:16px; margin-bottom:20px;">
        <strong>{t("🧬 争议洞察：")}</strong>{topic}
    </div>
    """, unsafe_allow_html=True)

    if guidance:
        st.markdown(f"""
        <div style="background:rgba(0,191,165,0.08); border-left:3px solid #00bfa5; border-radius:4px; padding:12px; margin-bottom:16px;">
            <small style="opacity:0.7;">{t("🎯 剖析争议点：")}</small><br>
            <strong>{guidance}</strong>
        </div>
        """, unsafe_allow_html=True)

    if not is_any_llm_configured():
        st.warning(t("⚠️ 未配置 LLM API Key。争议洞察需要 LLM 进行深度分析。将使用模板化输出。"))

    try:
        with st.spinner(t("🔍 正在搜集社交媒体讨论...")):
            start_time = datetime.now()

            # Step 1: Social-media-focused search
            search_results = _search_insight(topic)

        if not search_results:
            st.warning(t("未找到关于「{topic}」的社交媒体讨论，请尝试换一个关键词或更宽泛的表述。", topic=topic))
            st.caption(t("💡 提示：确保已在设置中配置搜索 API Key（如 Tavily），或尝试切换到 DuckDuckGo。"))
            return

        st.success(t("✅ 搜集到 {count} 条相关讨论", count=len(search_results)))

        # Step 2: Opinion camp analysis (LLM Call 1)
        with st.spinner(t("🧐 正在识别舆论阵营与情绪分布...")):
            opinion_data = _analyze_opinion_camps(topic, search_results, guidance)

        num_camps = len(opinion_data.get("camps", []))
        if num_camps > 0:
            camp_names = "、".join(c.get("name", "") for c in opinion_data["camps"])
            st.success(t("✅ 识别出 {num} 个舆论阵营：{names}", num=num_camps, names=camp_names))
        else:
            st.info(t("ℹ️ 未能清晰识别舆论阵营，将生成通用报告"))

        num_communities = len(opinion_data.get("communities", []))
        if num_communities > 0:
            st.caption(t("👥 涉及 {num} 个圈层/社区", num=num_communities))

        genes = opinion_data.get("controversy_genes", [])
        if genes:
            gene_tags = " · ".join(f"#{g.get('tag', '')}" for g in genes)
            st.caption(f"🏷️ {gene_tags}")

        # Step 3: Narrative report synthesis (LLM Call 2)
        with st.spinner(t("✍️ 正在撰写洞察报告...")):
            report = _synthesize_insight_report(topic, opinion_data, search_results)

        elapsed = (datetime.now() - start_time).total_seconds()
        st.caption(t("⏱️ 耗时 {elapsed:.0f} 秒", elapsed=elapsed))

        # Cache for redisplay on Q&A rerun
        st.session_state.current_insight_report = report
        st.session_state.current_insight_data = opinion_data

        _display_insight_result(topic, report, opinion_data)

    except Exception as e:
        logger.error(f"Insight mode failed for '{topic}': {e}")
        st.error(t("❌ 争议洞察分析出错：") + str(e)[:200])
        st.caption(t("请检查网络连接和 API 配置后重试。"))


def _search_insight(topic: str) -> list[dict]:
    """Social-media-focused search for controversy insight mode.
    Multiple parallel queries targeting different platforms and angles.
    Uses 90-day window (vs 30 for news) since social controversies evolve slowly.
    """
    from utils.search import bilingual_search
    from utils.search_providers import search_reddit

    queries = [
        f"{topic} 争议 讨论 看法",
        f"{topic} 网友评论 观点",
        f"{topic} 舆论 热议 两极",
        f"{topic} debate controversy reddit",
        f"{topic} viral outrage discussion",
    ]

    all_results = []

    # Chinese social queries (first 3)
    for q in queries[:3]:
        try:
            results = bilingual_search(
                query=q, max_results=6, search_depth="advanced",
                topic="news", days=90,
            )
            all_results.extend(results)
        except Exception:
            continue

    # English social queries (last 2)
    for q in queries[3:]:
        try:
            results = bilingual_search(
                query=q, max_results=4, search_depth="basic",
                topic="news", days=90,
            )
            all_results.extend(results)
        except Exception:
            continue

    # Reddit — best source for organic opinion camp analysis
    try:
        reddit_results = search_reddit(topic, max_results=8)
        all_results.extend(reddit_results)
    except Exception:
        pass

    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for r in all_results:
        url = r.get("url", "")
        if url:
            norm_url = url.split("?")[0]
            if norm_url not in seen_urls:
                seen_urls.add(norm_url)
                unique.append(r)
        else:
            unique.append(r)

    logger.info(f"Insight search for '{topic[:30]}': {len(unique)} unique from {len(all_results)} raw")
    return unique[:25]


def _analyze_opinion_camps(topic: str, search_results: list[dict], guidance: str = "") -> dict:
    """LLM Call 1: Analyze raw search results to extract full opinion landscape.
    Returns structured JSON with topic_type, camps, communities, genes, timeline, platform sentiment, etc.
    """
    if not is_any_llm_configured():
        return {"camps": [], "communities": [], "controversy_genes": [],
                "timeline": [], "opinion_shifts": [], "cross_platform_sentiment": {},
                "sentiment_distribution": {}, "topic_intro": "", "is_meme": False,
                "topic_type": "controversy"}

    from config import create_integration_llm
    llm = create_integration_llm(temperature=0.2)

    # Format search results with platform tags and dates for LLM
    items = []
    for i, r in enumerate(search_results[:20]):
        title = r.get("title", "")
        content = r.get("content", "")[:350]
        source = r.get("source", "")
        url = r.get("url", "").lower()
        # Platform detection
        if "reddit" in url:
            platform = "Reddit"
        elif "weibo" in url:
            platform = "微博"
        elif "zhihu" in url:
            platform = "知乎"
        elif "xiaohongshu" in url:
            platform = "小红书"
        elif "bilibili" in url:
            platform = "B站"
        elif "tieba.baidu" in url:
            platform = "百度贴吧"
        elif "douban" in url:
            platform = "豆瓣"
        elif "x.com" in url or "twitter" in url:
            platform = "X/Twitter"
        elif "youtube" in url:
            platform = "YouTube"
        elif "facebook" in url:
            platform = "Facebook"
        elif "instagram" in url:
            platform = "Instagram"
        elif "tiktok" in url:
            platform = "TikTok"
        else:
            platform = source or t("通用")
        # Try to extract date from content
        import re
        date_match = re.search(r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日号]?)", content[:200])
        date_str = f" [{date_match.group(1)}]" if date_match else ""
        items.append(f"[{i+1}] ({platform}){date_str} {title}\n  {content}")

    items_text = "\n\n".join(items)

    prompt = t("prompt.insight.analyze_opinion", topic=topic, items_text=items_text)
    if guidance:
        prompt += f"\n\n⚠️ 用户特别说明：{guidance}\n请在分析时重点关注用户希望了解的方面。"

    try:
        resp = llm.call(messages=[{"role": "user", "content": prompt}])
        import json as _json, re as _re
        # Try extracting from markdown code block first
        json_match = _re.search(r'```(?:json)?\s*\n?(.*?)\n?```', resp, _re.DOTALL)
        if json_match:
            return _json.loads(json_match.group(1))
        # Try finding JSON object
        brace_start = resp.find("{")
        brace_end = resp.rfind("}")
        if brace_start != -1 and brace_end > brace_start:
            return _json.loads(resp[brace_start:brace_end + 1])
        logger.warning(f"Failed to parse opinion camp JSON: {resp[:200]}")
        return {}
    except Exception as e:
        logger.warning(f"Opinion camp analysis failed: {e}")
        return {}


def _synthesize_insight_report(topic: str, opinion_data: dict, search_results: list[dict]) -> str:
    """LLM Call 2: Synthesize opinion data into a natural narrative report.
    No rigid template — writes like a social observation article.
    """
    if not is_any_llm_configured() or not opinion_data.get("camps"):
        return _template_insight_report(topic, opinion_data)

    from config import create_integration_llm
    llm = create_integration_llm(temperature=0.3)

    import json as _json
    analysis_json = _json.dumps(opinion_data, ensure_ascii=False, indent=2)

    # Gather raw quotes for color
    quote_lines = []
    for r in search_results[:6]:
        title = r.get("title", "")
        content = r.get("content", "")[:200]
        url = r.get("url", "").lower()
        if "reddit" in url:
            plat = " [Reddit]"
        elif "weibo" in url:
            plat = " [微博]"
        elif "zhihu" in url:
            plat = " [知乎]"
        elif "xiaohongshu" in url:
            plat = " [小红书]"
        elif "bilibili" in url:
            plat = " [B站]"
        elif "douban" in url:
            plat = " [豆瓣]"
        else:
            plat = ""
        quote_lines.append(f"- 「{title}」{plat}\n  {content}")
    quotes_text = "\n\n".join(quote_lines)

    is_meme = opinion_data.get("is_meme", False)
    meme_section = ""
    if is_meme:
        mi = opinion_data.get("meme_info", {})
        meme_section = f"""
特别说明：这是一个网络梗/流行语类话题。请在报告中包含梗的起源（{mi.get('origin', '未知')}）、
传播路径（{mi.get('evolution', '未知')}）和语义演变，用「梗百科」的风格自然叙述。"""

    topic_type = opinion_data.get("topic_type", "controversy")
    prompt = t("prompt.insight.synthesize_report", topic=topic, topic_type=topic_type,
               analysis_json=analysis_json, meme_section=meme_section, quotes_text=quotes_text)

    try:
        return llm.call(messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        logger.warning(f"Insight report synthesis failed: {e}")
        return _template_insight_report(topic, opinion_data)


def _template_insight_report(topic: str, opinion_data: dict) -> str:
    """Fallback template when LLM is unavailable."""
    camps = opinion_data.get("camps", [])
    genes = opinion_data.get("controversy_genes", [])
    communities = opinion_data.get("communities", [])
    timeline = opinion_data.get("timeline", [])

    lines = [f"# {t('🧬 争议洞察：')}{topic}\n"]

    intro = opinion_data.get("topic_intro", "")
    if intro:
        lines.append(f"{intro}\n")

    if camps:
        lines.append(f"## {t('template.camps_title', count=len(camps))}\n")
        for i, camp in enumerate(camps, 1):
            name = camp.get('name', t('未知'))
            size = camp.get('size_estimate', '?')
            lines.append(t("template.camp_item", i=i, name=name, size=size))
            lines.append(t("template.camp_profile", val=camp.get('audience_profile', '')))
            lines.append(t("template.camp_belief", val=camp.get('core_beliefs', '')))
            args = camp.get("key_arguments", [])
            if args:
                lines.append(t("template.camp_args", val='; '.join(args)))
            lines.append(t("template.camp_tone", val=camp.get('emotional_tone', '')))
            quote = camp.get("representative_quote", "")
            if quote:
                lines.append(t("template.camp_quote", val=quote))
            lines.append("")

    if communities:
        lines.append(f"## {t('template.communities_title')}\n")
        for c in communities:
            lines.append(t("template.community_item", name=c.get('name', ''), perspective=c.get('perspective', ''), camp=c.get('aligned_camp', t('未知'))))
        lines.append("")

    if timeline:
        lines.append(f"## {t('template.timeline_title')}\n")
        for t_event in sorted(timeline, key=lambda x: x.get("date", "")):
            lines.append(f"- **{t_event.get('date', '')}** — {t_event.get('event', '')} [{t_event.get('significance', '')}]")
        lines.append("")

    if genes:
        lines.append(f"## {t('template.genes_title')}\n")
        for g in genes:
            lines.append(f"- **#{g.get('tag', '')}**: {g.get('explanation', '')}")
        lines.append("")

    tension = opinion_data.get("underlying_tension", "")
    if tension:
        lines.append(f"## {t('template.tension_title')}\n\n{tension}\n")

    lines.append(f"\n> {t('⚠️ 模板化摘要。配置 LLM API Key 可启用 AI 智能深度分析。')}")
    return "\n".join(lines)


def _display_insight_result(topic: str, report: str, insight_data: dict):
    """Display an insight mode report with metadata and enhanced dashboard."""
    llm = st.session_state.get("integration_llm_provider", "")
    model = st.session_state.get("integration_llm_model", "")
    model_short = model.split("/")[-1] if "/" in model else model
    topic_type = insight_data.get("topic_type", "controversy")
    is_zh = st.session_state.get("lang", "zh") == "zh"
    type_labels = {
        "controversy": t("争议洞察"),
        "meme": "梗洞察" if is_zh else "Meme Insight",
        "event": "事件洞察" if is_zh else "Event Insight",
        "phenomenon": "现象洞察" if is_zh else "Phenomenon Insight",
    }
    type_label = type_labels.get(topic_type, t("争议洞察"))
    st.markdown(f"""
    <div style="text-align:right; opacity:0.5; font-size:12px; margin-bottom:16px;">
        {type_label} | {model_short}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown(report, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Dashboard
    _render_insight_dashboard(insight_data, topic)

    # Save
    _save_insight_report(topic, report, insight_data)

    # Follow-up Q&A
    _render_followup_qa(topic, report, mode="insight")

    # Upgrade to full controversy analysis
    st.divider()
    st.markdown(t("### ⚔️ 争议剖析"))
    st.caption(t("如果你对上述事件有疑问，请在下方输入你希望剖析的具体争议观点："))
    user_angle = st.text_area(
        t("请输入你想剖析的争议点..."),
        placeholder=t("例如：甲方称赔偿3亿但财报显示仅1亿，真实金额是多少？"),
        label_visibility="collapsed",
        key=f"insight_controversy_angle_{topic[:20]}",
    )
    if st.button(t("⚔️ 开始争议剖析"), type="primary", use_container_width=True, key="insight_upgrade"):
        if not user_angle.strip():
            st.warning(t("请输入你想剖析的争议点"))
        elif not is_any_llm_configured():
            st.error(t("⚠️ 未配置 LLM API Key，无法运行争议分析。请在设置中配置 API Key。"))
        else:
            with st.spinner(t("正在验证争议点与事件的相关性...")):
                is_relevant, reason = _validate_controversy_angle(topic, report, user_angle.strip())
            if is_relevant:
                st.session_state.analyze_mode = "controversy"
                st.session_state.controversy_angle = user_angle.strip()
                st.rerun()
            else:
                st.warning(f"{t('⚠️ 争议点与事件无关')}：{reason}\n\n{t('你提出的争议点与当前事件似乎无关，请重新描述。')}")


def _render_insight_dashboard(insight_data: dict, topic: str):
    """Render the enhanced insight dashboard with all 6 enhancements."""
    if not insight_data:
        return

    camps = insight_data.get("camps", [])
    genes = insight_data.get("controversy_genes", [])
    communities = insight_data.get("communities", [])
    timeline = insight_data.get("timeline", [])
    opinion_shifts = insight_data.get("opinion_shifts", [])
    cross_platform = insight_data.get("cross_platform_sentiment", {})
    sentiment = insight_data.get("sentiment_distribution", {})
    controversy_type = insight_data.get("controversy_type", "")
    underlying_tension = insight_data.get("underlying_tension", "")
    is_meme = insight_data.get("is_meme", False)
    topic_type = insight_data.get("topic_type", "controversy")

    st.divider()
    st.markdown(f"### {t('### 📊 争议洞察仪表盘').lstrip('#').strip()}")
    st.caption(t("⚠️ 以下数值为 AI 基于搜索结果的**定性估算**，非精确统计数据，仅供参考舆论格局"))

    # ---- Row 0: Tags (adapt label based on topic_type) ----
    if isinstance(genes, list) and genes:
        _render_controversy_genes(genes)
    elif topic_type == "meme":
        meme_tags = insight_data.get("meme_info", {})
        if meme_tags.get("variants"):
            tag_html = "".join(
                f'<span class="badge badge-controversy" style="margin:2px;">{v}</span>'
                for v in meme_tags["variants"][:5]
            )
            st.markdown(f"{t('🏷️ 梗的标签：')}{tag_html}", unsafe_allow_html=True)

    # ---- Row 1: Key Metrics (adapt based on topic_type) ----
    if topic_type == "meme":
        col1, col2, col3 = st.columns(3)
        with col1:
            num_timeline = len(timeline)
            st.metric(t("关键节点"), f"{num_timeline}{t(' 个')}" if num_timeline else "—")
        with col2:
            num_communities = len(communities)
            st.metric(t("涉及圈层"), f"{num_communities}{t(' 个')}" if num_communities else "—")
        with col3:
            num_camps = len(camps)
            st.metric(t("观点类型"), f"{num_camps}{t(' 种')}" if num_camps else "—")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t("舆论阵营"), f"{len(camps)}{t(' 个')}")
        with col2:
            num_communities = len(communities)
            st.metric(t("涉及圈层"), f"{num_communities}{t(' 个')}" if num_communities else "—")
        with col3:
            num_timeline = len(timeline)
            st.metric(t("关键节点"), f"{num_timeline}{t(' 个')}" if num_timeline else "—")
        with col4:
            st.metric(t("争议类型"), controversy_type[:10] if controversy_type else t("待分析"))

    if is_meme:
        st.caption(t("🧬 已识别为梗/网络流行语类话题 — 报告包含梗百科溯源"))

    # ---- Row 2: Camp Size Chart + Sentiment Distribution ----
    col_l, col_r = st.columns(2)
    with col_l:
        if isinstance(camps, list) and camps and any(
            isinstance(c, dict) and c.get("size_estimate", 0) > 0 for c in camps
        ):
            _render_camp_size_chart(camps)
        else:
            st.markdown("""
            <div style="text-align:center; padding:60px 20px; opacity:0.4;">
                <p style="font-size:14px; font-weight:600;">{t('舆论阵营规模分布')}</p>
                <p style="font-size:13px;">{t('暂无数据')}</p>
            </div>
            """, unsafe_allow_html=True)
    with col_r:
        from ui.components import sentiment_bar_chart
        chart_data = {}
        if isinstance(sentiment, dict):
            for k, v in sentiment.items():
                if isinstance(v, (int, float)):
                    chart_data[k] = v / 100.0 if v > 1 else v
        if chart_data:
            sentiment_bar_chart(chart_data)
        else:
            st.markdown(f"""
            <div style="text-align:center; padding:60px 20px; opacity:0.4;">
                <p style="font-size:14px; font-weight:600;">{t('情绪分布')}</p>
                <p style="font-size:13px;">{t('暂无数据')}</p>
            </div>
            """, unsafe_allow_html=True)

    # ---- Row 3: Platform Radar + Communities Table ----
    col_l2, col_r2 = st.columns(2)
    with col_l2:
        has_platform_data = False
        if isinstance(cross_platform, dict) and len(cross_platform) >= 2:
            try:
                has_platform_data = any(
                    isinstance(pdata, dict) and any(
                        isinstance(v, (int, float)) and v > 0 for v in pdata.values()
                    )
                    for pdata in cross_platform.values()
                )
            except Exception:
                has_platform_data = False
        if has_platform_data:
            _render_platform_radar(cross_platform)
        else:
            st.markdown(f"""
            <div style="text-align:center; padding:60px 20px; opacity:0.4;">
                <p style="font-size:14px; font-weight:600;">{t('跨平台情绪对比')}</p>
                <p style="font-size:13px;">{t('暂无数据')}</p>
            </div>
            """, unsafe_allow_html=True)
    with col_r2:
        if isinstance(communities, list) and communities:
            _render_communities_table(communities)

    # ---- Row 4: Timeline ----
    if isinstance(timeline, list) and timeline and any(
        isinstance(t, dict) and t.get("event") for t in timeline
    ):
        _render_timeline(timeline)

    # ---- Row 5: Opinion Shifts ----
    if isinstance(opinion_shifts, list) and opinion_shifts:
        st.markdown(f"#### {t('#### 🔄 观点迁移').lstrip('#').strip()}")
        for shift in opinion_shifts:
            trigger = shift.get("trigger", "")
            approx_date = shift.get("approx_date", "")
            date_str = f"（{approx_date}）" if approx_date else ""
            st.markdown(f"""
            <div style="padding:8px 12px; margin:6px 0; border-left:3px solid #f0a500; background:rgba(240,165,0,0.06); border-radius:0 6px 6px 0;">
                <strong>{shift.get('from', '')}</strong> → <strong>{shift.get('to', '')}</strong> {date_str}<br>
                <span style="opacity:0.7; font-size:13px;">📌 {trigger}</span>
            </div>
            """, unsafe_allow_html=True)

    # ---- Row 6: Underlying Tension ----
    if underlying_tension:
        st.markdown(f"#### {t('#### 🧠 深层矛盾洞察').lstrip('#').strip()}")
        st.info(underlying_tension)


def _render_controversy_genes(genes: list[dict]):
    """Render controversy gene tags as colored HTML badges."""
    gene_colors = {
        "代际冲突": "#d63384", "阶层焦虑": "#fd7e14", "性别议题": "#e83e8c",
        "身份政治": "#6f42c1", "文化差异": "#20c997", "利益冲突": "#dc3545",
        "价值观对立": "#0d6efd", "圈层隔阂": "#6c757d",
    }
    badges_html = " ".join(
        f'<span style="display:inline-block; padding:4px 12px; margin:3px; '
        f'border-radius:20px; font-size:13px; font-weight:600; '
        f'background:{gene_colors.get(g.get("tag", ""), "#6c757d")}22; '
        f'color:{gene_colors.get(g.get("tag", ""), "#6c757d")}; '
        f'border:1px solid {gene_colors.get(g.get("tag", ""), "#6c757d")}44;">'
        f'#{g.get("tag", "")}</span>'
        for g in genes
    )
    st.markdown(f"""
    <div style="margin-bottom:16px;">
        <span style="font-size:14px; font-weight:600; opacity:0.7;">🏷️ 争议基因：</span>
        {badges_html}
    </div>
    """, unsafe_allow_html=True)

    # Explanation in expander
    with st.expander(t("📖 基因标签解读")):
        for g in genes:
            st.markdown(f"- **#{g.get('tag', '')}**：{g.get('explanation', '')}")


def _render_camp_size_chart(camps: list[dict]):
    """Render a bar chart of opinion camp size estimates."""
    import plotly.graph_objects as go
    names = [c.get("name") or t("未知阵营") for i, c in enumerate(camps)]
    sizes = [c.get("size_estimate", 0) for c in camps]
    tones = [c.get("emotional_tone", "") for c in camps]
    colors = ["#00bfa5", "#d63384", "#f0a500", "#0d6efd", "#fd7e14"]

    fig = go.Figure(go.Bar(
        x=names, y=sizes,
        marker=dict(color=colors[:len(sizes)]),
        text=[f"{s}%" for s in sizes],
        textposition="outside",
        hovertemplate="%{x}<br>占比: %{y}%<br>情绪: %{customdata}<extra></extra>",
        customdata=tones,
    ))
    fig.update_layout(
        title={"text": t("舆论阵营规模分布（AI 估算）"), "font": {"size": 16}},
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis={"title": t("估计占比 (%)"), "range": [0, max(sizes) * 1.3], "showgrid": True, "gridcolor": "rgba(128,128,128,0.1)"},
        margin=dict(l=20, r=20, t=40, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(t("阵营占比由 AI 估算，不代表精确统计数据"))


def _render_platform_radar(cross_platform: dict):
    """Render a radar/spider chart comparing sentiment across platforms."""
    import plotly.graph_objects as go

    platforms = list(cross_platform.keys())
    # Collect all sentiment dimensions
    all_dims = set()
    for pdata in cross_platform.values():
        all_dims.update(pdata.keys())
    all_dims = sorted(all_dims)

    if len(all_dims) < 2:
        return

    fig = go.Figure()
    palette = ["#00bfa5", "#d63384", "#f0a500", "#0d6efd", "#fd7e14", "#6f42c1", "#20c997"]
    for i, platform in enumerate(platforms):
        pdata = cross_platform[platform]
        values = [pdata.get(d, 0) for d in all_dims]
        values.append(values[0])  # Close the polygon
        dims_closed = all_dims + [all_dims[0]]
        fig.add_trace(go.Scatterpolar(
            r=values, theta=dims_closed, name=platform,
            fill="toself", opacity=0.35,
            marker=dict(color=palette[i % len(palette)]),
        ))

    fig.update_layout(
        title={"text": t("跨平台情绪对比（AI 估算）"), "font": {"size": 16}},
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            radialaxis=dict(range=[0, 100], showticklabels=True, ticks="",
                          gridcolor="rgba(128,128,128,0.15)"),
            angularaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_timeline(timeline: list[dict]):
    """Render a controversy timeline using Plotly scatter + lines."""
    import plotly.graph_objects as go

    sorted_tl = sorted(timeline, key=lambda x: x.get("date", ""))

    events = [t.get("event", "") for t in sorted_tl]
    dates = [t.get("date", "") for t in sorted_tl]
    heats = [t.get("heat") or 0 for t in sorted_tl]
    significances = [t.get("significance", "") for t in sorted_tl]

    # Color by significance type
    sig_colors = []
    for s in significances:
        if "引爆" in s:
            sig_colors.append("#dc3545")
        elif "反转" in s:
            sig_colors.append("#f0a500")
        elif "平息" in s:
            sig_colors.append("#00bfa5")
        else:
            sig_colors.append("#0d6efd")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=heats, mode="lines+markers",
        marker=dict(size=[max(h / 5, 8) for h in heats], color=sig_colors,
                   line=dict(width=1, color="rgba(255,255,255,0.3)")),
        line=dict(color="#6c757d", width=1, dash="dot"),
        text=events,
        hovertemplate="%{x}<br>%{text}<br>热度: %{y}<extra></extra>",
    ))
    fig.update_layout(
        title={"text": t("争议演变时间线（AI 梳理）"), "font": {"size": 16}},
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"showgrid": False},
        yaxis={"title": t("热度"), "range": [0, 110], "showgrid": True, "gridcolor": "rgba(128,128,128,0.1)"},
        margin=dict(l=20, r=20, t=40, b=60),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Legend for significance colors
    st.caption(t("🔴 引爆点  🟠 反转  🔵 升级  🟢 平息"))


def _render_communities_table(communities: list[dict]):
    """Render a table showing communities and their perspectives."""
    st.markdown(f"#### {t('#### 🎯 圈层视角').lstrip('#').strip()}")

    header = f"""
    <div style="display:grid; grid-template-columns:1fr 1.5fr 1fr; gap:8px; padding:8px 12px;
        border-bottom:1px solid rgba(128,128,128,0.15); font-size:12px; opacity:0.6; font-weight:600;">
        <span>{t('圈层')}</span><span>{t('独特视角')}</span><span>{t('倾向阵营')}</span>
    </div>
    """
    st.markdown(header, unsafe_allow_html=True)

    for c in communities:
        st.markdown(f"""
        <div style="display:grid; grid-template-columns:1fr 1.5fr 1fr; gap:8px; padding:6px 12px;
            border-bottom:1px solid rgba(128,128,128,0.05); font-size:13px;">
            <strong>{c.get('name', '')}</strong>
            <span style="opacity:0.8;">{c.get('perspective', '')}</span>
            <span style="opacity:0.6;">→ {c.get('aligned_camp', '—')}</span>
        </div>
        """, unsafe_allow_html=True)


def _save_insight_report(topic: str, report: str, insight_data: dict):
    """Save an insight-mode report to persistence."""
    try:
        from utils.persistence import save_report
        save_report(topic, report)
    except Exception as e:
        logger.warning(f"Failed to save insight report: {e}")


# ============================================================
# Info Mode
# ============================================================

def _run_info_mode(topic: str):
    st.markdown(f"""
    <div style="border:1px solid rgba(128,128,128,0.15); border-radius:8px; padding:16px; margin-bottom:20px;">
        <strong>{t("📋 资讯梳理：")}</strong>{topic}
    </div>
    """, unsafe_allow_html=True)
    with st.spinner(t("🔍 正在搜集相关信息...")):
        search_results = _search_info(topic)

    if not search_results:
        st.warning(t("未搜索到任何结果，请尝试用更具体的关键词。"))
        if st.button(t("← 返回首页重新搜索"), use_container_width=True):
            st.session_state.pop("current_topic", None)
            st.session_state.pop("current_mode", None)
            st.session_state.current_page = "feed"
            st.rerun()
        return

    # Filter irrelevant results
    original_results = list(search_results)
    if is_any_llm_configured() and len(search_results) > 3:
        with st.spinner(t("🔍 正在筛选与事件相关的信息来源...")):
            search_results = _filter_relevant(topic, search_results)

    # If all filtered out, show the raw search results as candidates
    if not search_results:
        st.warning(t("搜索到的结果似乎与「{topic}」不直接相关。以下是原始搜索结果，请选择最接近的事件：", topic=topic))
        _show_search_candidates(original_results)
        if st.button(t("← 返回首页重新搜索"), use_container_width=True):
            st.session_state.pop("current_topic", None)
            st.session_state.pop("current_mode", None)
            st.session_state.current_page = "feed"
            st.rerun()
        return

    with st.spinner(t("📝 正在梳理信息...")):
        summary = _summarize_info(topic, search_results)

    # Cache for redisplay
    st.session_state.current_summary = summary
    st.session_state.current_search_results = search_results

    _display_info_result(topic, summary, search_results)


def _display_controversy_report(topic: str, report: str):
    """Display a controversy report with metadata."""
    elapsed_str = ""
    llm = st.session_state.get("integration_llm_provider", "")
    model = st.session_state.get("integration_llm_model", "")
    model_short = model.split("/")[-1] if "/" in model else model
    mode_label = "Live AI" if is_any_llm_configured() else "未配置 LLM"
    st.markdown(f"""
    <div style="text-align:right; opacity:0.5; font-size:12px; margin-bottom:16px;">
        {elapsed_str} | {model_short} | {mode_label}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown(report, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _display_info_result(topic: str, summary: str, search_results: list):
    """Display info mode results."""
    st.markdown(f"### {t('### 📋 信息梳理结果').lstrip('#').strip()}")
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown(summary, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander(t("📎 信息来源列表")):
        for i, r in enumerate(search_results[:10]):
            title = r.get("title", t("无标题"))
            url = r.get("url", "")
            source = r.get("source", "").strip()
            if source:
                st.markdown(f"{i+1}. **{title}** — *{source}*")
            else:
                st.markdown(f"{i+1}. **{title}**")
            if url:
                st.caption(url)

    _render_info_dashboard(topic, search_results)
    _save_report(topic, summary)
    _render_followup_qa(topic, summary, mode="info")

    # ---- Controversy Analysis Upgrade ----
    st.divider()
    st.markdown(t("### ⚔️ 争议剖析"))
    st.caption(t("如果你对上述事件有疑问，请在下方输入你希望剖析的具体争议观点："))
    user_angle = st.text_area(
        t("请输入你想剖析的争议点..."),
        placeholder=t("例如：甲方称赔偿3亿但财报显示仅1亿，真实金额是多少？"),
        label_visibility="collapsed",
        key=f"controversy_angle_input_{topic[:20]}",
    )
    if st.button(t("⚔️ 开始争议剖析"), type="primary", use_container_width=True):
        if not user_angle.strip():
            st.warning(t("请输入你想剖析的争议点"))
        elif not is_any_llm_configured():
            st.error(t("⚠️ 未配置 LLM API Key，无法运行争议分析。请在设置中配置 API Key。"))
        else:
            with st.spinner(t("正在验证争议点与事件的相关性...")):
                is_relevant, reason = _validate_controversy_angle(topic, summary, user_angle.strip())
            if is_relevant:
                st.session_state.analyze_mode = "controversy"
                st.session_state.controversy_angle = user_angle.strip()
                st.rerun()
            else:
                st.warning(f"{t('⚠️ 争议点与事件无关')}：{reason}\n\n{t('你提出的争议点与当前事件似乎无关，请重新描述。')}")


def _validate_controversy_angle(topic: str, summary: str, angle: str) -> tuple[bool, str]:
    """Check if the user's controversy angle is related to the event. Returns (is_relevant, reason)."""
    try:
        from config import create_search_llm
        llm = create_search_llm(temperature=0.0)
        result = llm.call(messages=[{"role": "user", "content": t(
            "prompt.validate_controversy", summary=summary[:1500], angle=angle
        )}])
        result = result.strip()
        if result.startswith("```"):
            lines = result.split("\n")
            result = "\n".join(lines[1:]) if len(lines) > 1 else result
            if result.endswith("```"):
                result = result[:-3]
        import json
        data = json.loads(result)
        return data.get("relevant", False), data.get("reason", "")
    except Exception:
        # If validation fails (e.g. no LLM), allow the analysis to proceed
        return True, ""


# ============================================================
# Search & Summarize
# ============================================================

def _search_info(topic: str) -> list[dict]:
    try:
        from utils.search import bilingual_search
        results = bilingual_search(
            query=topic, max_results=12, search_depth="advanced",
            topic="news", days=30,
        )
        logger.info(f"Bilingual search for '{topic[:30]}': {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"Search failed: {e}")
        st.error(f"{t('搜索失败：')}{e}")

    return []


def _filter_relevant(topic: str, results: list[dict]) -> list[dict]:
    """Use LLM to filter out search results unrelated to the topic.
    If ALL results are unrelated, returns empty list so caller can handle.
    """
    if not results:
        return results
    try:
        from config import create_search_llm
        llm = create_search_llm(temperature=0.0)

        items = "\n".join(
            f"{i+1}. {r.get('title', '')} | {r.get('content', '')[:100]}"
            for i, r in enumerate(results)
        )

        prompt = t("prompt.filter_relevant", topic=topic, items=items)

        resp = llm.call(messages=[{"role": "user", "content": prompt}]).strip()
        if resp.upper() == "NONE":
            return []  # ALL irrelevant — let caller present candidates

        indices = set()
        for part in resp.split(","):
            part = part.strip().strip(".")
            if part.isdigit():
                indices.add(int(part) - 1)

        return [r for i, r in enumerate(results) if i in indices]
    except Exception as e:
        logger.warning(f"Relevance filter failed: {e}")
        return results  # On error, keep all


def _show_search_candidates(results: list[dict]):
    """Show raw search results as clickable candidates."""
    import re
    for i, r in enumerate(results[:6]):
        title = r.get("title", "")
        content = r.get("content", "")[:150]
        source = r.get("source", "").strip()
        url = r.get("url", "")
        date_match = re.search(r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日号]?)", content)
        date_str = f" · {date_match.group(1)}" if date_match else ""
        summary = content.split("。")[0] if "。" in content else content[:100]

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="cyber-card" style="padding:12px; margin-bottom:8px;">
                <strong>{title}</strong>
                <p style="opacity:0.7; font-size:13px; margin:4px 0;">{summary}{date_str}</p>
                <span style="font-size:11px; opacity:0.5;">📍 {source or '未署名'}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button(t("选这个"), key=f"cand_{i}", use_container_width=True):
                st.session_state.analyze_topic = title
                st.session_state.analyze_mode = "info"
                st.rerun()


def _summarize_info(topic: str, search_results: list[dict]) -> str:
    if is_any_llm_configured() and search_results:
        try:
            from config import create_integration_llm
            llm = create_integration_llm(temperature=0.1)

            sources_text = "\n\n---\n\n".join(
                f"来源{i+1}: {r.get('source', '')}\n标题: {r.get('title', '')}\n内容: {r.get('content', '')[:500]}"
                for i, r in enumerate(search_results[:8])
            )

            prompt = t("prompt.summarize_info", topic=topic, sources_text=sources_text)

            return llm.call(messages=[{"role": "user", "content": prompt}])
        except Exception as e:
            logger.warning(f"LLM summary failed: {e}")

    lines = [f"## 📋 {topic}\n", "### 信息概述\n"]
    for i, r in enumerate(search_results[:5]):
        title = r.get("title", "无标题")
        content = r.get("content", "")[:200]
        source = r.get("source", "").strip()
        src_line = f"*来源: {source}*" if source else ""
        lines.append(f"**{title}**\n\n{content}\n\n{src_line}\n")
    lines.append("\n> ⚠️ 模板化摘要。配置 LLM API Key 可启用 AI 智能梳理。")
    return "\n".join(lines)


# ============================================================
# Live / Mock Analysis (Controversy Mode)
# ============================================================

def _run_live_analysis(topic: str, controversy_angle: str = "", existing_info: str = "", intent: str = "debate_understanding") -> str | None:
    try:
        from agents.crew import run_analysis
        report = run_analysis(topic, controversy_angle, existing_info, intent)
        return str(report)
    except Exception as e:
        logger.error(f"Live analysis failed: {e}")
        st.error(f"{t('AI 分析出现错误：')}{str(e)}")
        return None


# ============================================================
# Persistence
# ============================================================

def _save_report(topic: str, report: str):
    try:
        import re
        from utils.persistence import save_report
        prob_match = re.search(r"真相可能概率\s*\|\s*([\d.]+)%", report)
        truth_prob = float(prob_match.group(1)) if prob_match else None
        if truth_prob is not None and not (0 <= truth_prob <= 100):
            truth_prob = min(max(truth_prob, 0), 100) if truth_prob > 100 else (truth_prob * 100 if truth_prob < 1 else None)
        save_report(topic, report, truth_prob)
    except Exception as e:
        logger.warning(f"Failed to save report: {e}")


# ============================================================
# Embedded Dashboards
# ============================================================

def _render_controversy_dashboard(report: str, topic: str, intent: str = "debate_understanding"):
    import re
    from ui.components import truth_probability_gauge, sentiment_bar_chart

    is_truth_seeking = (intent == "truth_seeking")

    if is_truth_seeking:
        prob_match = re.search(r"真相可能概率\s*\|\s*([\d.]+)%", report)
        truth_prob = float(prob_match.group(1)) if prob_match else None
        if truth_prob is not None and not (0 <= truth_prob <= 100):
            truth_prob = min(max(truth_prob, 0), 100) if truth_prob > 100 else (truth_prob * 100 if truth_prob < 1 else None)
        ev_match = re.search(r"证据链完整度\s*\|\s*([\d.]+)\s*/\s*100", report)
        evidence_score = int(ev_match.group(1)) if ev_match else None
    else:
        truth_prob = None
        evidence_score = None

    sources = len(re.findall(r"\[来源:", report))

    if is_truth_seeking:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t("真相可能概率"), f"{truth_prob}%" if truth_prob is not None else t("暂无数据"))
        with col2:
            st.metric(t("证据链完整度"), f"{evidence_score}/100" if evidence_score is not None else t("暂无数据"))
        with col3:
            st.metric(t("引用来源数"), str(sources))
    else:
        # Debate understanding: show source count + debate landscape label
        col1, col2 = st.columns(2)
        with col1:
            st.metric(t("引用来源数"), str(sources))
        with col2:
            # Count stakeholder groups mentioned in report
            camp_count = len(re.findall(r"###\s+", report))
            st.metric(t("📊 争议格局"), str(max(camp_count, 1)))

    if is_truth_seeking:
        col_l, col_r = st.columns(2)
        with col_l:
            truth_probability_gauge(truth_prob)
        with col_r:
            sentiment_data = _extract_sentiment(report)
            if sentiment_data:
                sentiment_bar_chart(sentiment_data)
            else:
                st.markdown(f"""
                <div style="text-align:center; padding:60px 20px; opacity:0.4;">
                    <p>{t('评论区情绪分布')}</p>
                    <p style="font-size:13px;">{t('暂无数据')}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Debate understanding: just show sentiment chart full-width
        sentiment_data = _extract_sentiment(report)
        if sentiment_data:
            sentiment_bar_chart(sentiment_data)
        else:
            st.caption(t("暂无数据"))


def _render_info_dashboard(topic: str, search_results: list[dict]):
    if not search_results:
        return
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t("信息来源数"), str(len(search_results)))
    with col2:
        sources = set(r.get("source", "") for r in search_results if r.get("source"))
        st.metric(t("独立来源"), str(len(sources)))
    with col3:
        total = sum(len(r.get("content", "")) for r in search_results)
        st.metric(t("信息量"), f"{total // 100}{t('条')}")

    st.markdown(f"#### {t('#### 来源分布').lstrip('#').strip()}")
    source_counts = {}
    for r in search_results:
        src = r.get("source", "").strip()[:30] or f"({t('未署名')})"
        source_counts[src] = source_counts.get(src, 0) + 1
    for src, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        st.markdown(f"""
        <div style="display:flex; align-items:center; margin:8px 0; gap:12px;">
            <span style="flex:1; font-size:14px;">{src}</span>
            <div style="flex:1; height:6px; border-radius:3px; background:rgba(128,128,128,0.15);">
                <div style="width:{count/len(search_results)*100}%; height:100%; border-radius:3px; background:#00bfa5;"></div>
            </div>
            <span style="font-size:13px; opacity:0.6;">{count}{t('篇')}</span>
        </div>
        """, unsafe_allow_html=True)


def _extract_sentiment(report: str) -> dict:
    import re
    sentiment = {}
    patterns = {
        "angry": r"愤怒.*?(\d+)%", "fearful": r"恐惧.*?(\d+)%",
        "neutral": r"中立.*?(\d+)%", "supportive": r"支持.*?(\d+)%",
        "sympathetic": r"同情.*?(\d+)%", "sarcastic": r"讽刺.*?(\d+)%",
    }
    for key, pat in patterns.items():
        match = re.search(pat, report)
        if match:
            sentiment[key] = int(match.group(1)) / 100
    return sentiment  # Return only extracted values; empty dict = no data


# ============================================================
# Follow-up Q&A
# ============================================================

def _render_followup_qa(topic: str, report_content: str, mode: str):
    """Collapsible AI follow-up Q&A panel after report display."""
    st.divider()

    # Init session state for Q&A
    qa_key = f"qa_history_{topic[:30]}"
    if qa_key not in st.session_state:
        st.session_state[qa_key] = []

    # Unique suffix to avoid key collision across modes
    qa_suffix = f"{mode}_{topic[:20]}"
    input_key = f"qa_input_{qa_suffix}"
    send_key = f"qa_send_{qa_suffix}"

    with st.expander(t("💬 追问 AI（对报告内容有疑问？点击展开对话）"), expanded=False):
        st.caption(t("就报告中的疑点、事件细节或相关背景进行追问，AI 会结合报告内容和实时搜索为你解答。"))

        # Chat history display
        for qa in st.session_state[qa_key]:
            st.markdown(t("""
            <div style="margin:8px 0; padding:8px 12px; border-radius:8px; background:rgba(0,191,165,0.06);">
                <strong>{you}</strong>{question}
            </div>
            <div style="margin:4px 0 12px 16px; padding:8px 12px; border-left:3px solid #00bfa5; opacity:0.85;">
                {answer}
            </div>
            """, you=t("🧑 你："), question=qa['question'], answer=qa['answer']), unsafe_allow_html=True)

        # Input — use a form to isolate submission from other buttons
        with st.form(key=f"qa_form_{qa_suffix}", clear_on_submit=True):
            col_input, col_send = st.columns([5, 1])
            with col_input:
                question = st.text_input(
                    t("输入追问..."),
                    placeholder=t("例如：这个事件的最初爆料者是谁？有权威第三方检测结果吗？"),
                    label_visibility="collapsed",
                    key=input_key,
                )
            with col_send:
                submitted = st.form_submit_button(t("发送"), use_container_width=True)

        if submitted and question.strip():
            with st.spinner(t("🤔 AI 正在思考（判断是否需要搜索补充信息）...")):
                need_search = _should_search(topic, report_content[:2000], question.strip())
            spinner_text = t("🤔 正在搜索补充信息并生成回答...") if need_search else t("🤔 正在基于现有信息生成回答...")
            with st.spinner(spinner_text):
                answer = _answer_followup(topic, report_content, question.strip(), mode, need_search=need_search)
            st.session_state[qa_key].append({"question": question.strip(), "answer": answer})
            st.rerun()


def _answer_followup(topic: str, report: str, question: str, mode: str,
                     need_search: bool = False) -> str:
    """Answer a follow-up question. Intelligently triggers search only when needed."""
    if not is_any_llm_configured():
        return t("⚠️ 未配置 LLM API Key，追问功能需要在 .env 中配置 API Key 后使用。")

    # Search if needed
    additional_context = ""
    if need_search:
        additional_context = _do_search(topic, question)

    # Answer
    return _generate_answer(topic, report, question, additional_context, need_search)


def _should_search(topic: str, report: str, question: str) -> bool:
    """Use LLM to decide if the question needs external search."""
    try:
        from config import create_search_llm
        llm = create_search_llm(temperature=0.0)

        prompt = t("prompt.should_search", topic=topic, report=report[:2000], question=question)

        result = llm.call(messages=[{"role": "user", "content": prompt}]).strip().upper()
        return "YES" in result
    except Exception as e:
        logger.warning(f"Search decision failed: {e}")
        # Fallback: search if question seems to ask for external info
        return any(kw in question for kw in ["最新", "来源", "链接", "哪里", "谁", "数据", "统计", "类似", "以前", "更多", "什么时候"])


def _do_search(topic: str, question: str) -> str:
    """Perform supplementary search for Q&A follow-up questions."""
    try:
        from config import get_active_domains
        from utils.search_providers import search as provider_search
        results = provider_search(
            query=f"{topic} {question}",
            max_results=3, domains=get_active_domains(),
            search_depth="basic", topic="news",
        )
        if not results:
            return ""
        return "\n".join(
            f"- {r.get('title', '')}: {r.get('content', '')[:200]}" for r in results
        )
    except Exception as e:
        logger.warning(f"Follow-up search failed: {e}")
        return ""


def _generate_answer(topic: str, report: str, question: str,
                     additional_context: str, did_search: bool) -> str:
    """Generate the final answer."""
    try:
        from config import create_integration_llm
        llm = create_integration_llm(temperature=0.3)

        search_note = ""
        if did_search:
            if additional_context:
                search_note = f"\n\n## 补充搜索信息\n{additional_context}\n\n如果搜索到的信息与问题相关，请引用。如果不相关或不足以回答，诚实说明。"
            else:
                search_note = "\n\n（已尝试搜索补充信息，但未找到相关结果。请基于报告内容回答，诚实说明信息不足的部分。）"

        prompt = t("prompt.generate_answer", topic=topic, report=report[:3000],
                   search_note=search_note, question=question)

        return llm.call(messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        return f"{t('追问处理失败：')}{str(e)}"


# ============================================================
# Topic Disambiguation
# ============================================================

def _disambiguate_topic(topic: str) -> str | None:
    """If keyword is too vague, search and present candidates to user.
    Returns the resolved topic, or None if waiting for user selection.
    """
    # Never disambiguate homepage news — they're already curated headlines
    if st.session_state.pop("from_feed", False):
        return topic

    # Skip for clearly specific topics
    if len(topic) > 20:
        return topic

    # Quick search
    try:
        from config import get_active_domains
        from utils.search_providers import search as provider_search
        results = provider_search(
            query=topic, max_results=6, domains=get_active_domains(),
            search_depth="basic", topic="news",
        )
    except Exception:
        return topic

    if len(results) < 2:
        return topic

    # Quick similarity check: if top result title contains most of the topic words, it's specific
    top_title = results[0].get("title", "")
    topic_words = set(topic.replace("，", " ").replace(",", " ").split())
    match_words = sum(1 for w in topic_words if w in top_title)
    if len(topic_words) >= 2 and match_words >= len(topic_words) * 0.5:
        return topic  # Good enough match, don't bother with LLM

    # Only run LLM check when results are clearly divergent
    titles = "\n".join(f"{i+1}. {r.get('title', '')}" for i, r in enumerate(results))
    try:
        from config import create_search_llm
        llm = create_search_llm(temperature=0.0)

        decision = llm.call(messages=[{"role": "user", "content": t("prompt.disambiguate", topic=topic, titles=titles)}]).strip().upper()

        if "SPECIFIC" in decision:
            return topic
    except Exception:
        return topic  # If LLM fails, proceed directly rather than blocking

    # Truly ambiguous — show candidates (should be rare now)
    st.markdown(f"### {t('🔍 你的关键词指向多个可能的事件，请选择一个：')}")

    seen = set()
    candidates = []
    for r in results:
        title = r.get("title", "").strip()
        if title and title not in seen and len(title) > 5:
            seen.add(title)
            candidates.append(r)
        if len(candidates) >= 5:
            break

    if len(candidates) <= 1:
        return topic

    st.info(t("🔍 关键词较模糊，以下是可能的事件候选，请选择一个："))
    selected = None
    for i, r in enumerate(candidates):
        title = r.get("title", "")
        content = r.get("content", "")[:150]
        source = r.get("source", "")
        # Try to extract date from content
        import re
        date_match = re.search(r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日号]?)", content)
        date_str = f" · {date_match.group(1)}" if date_match else ""

        # One-line summary from content
        summary = content.split("。")[0] if "。" in content else content[:100]

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="cyber-card" style="padding:12px; margin-bottom:8px;">
                <strong>{title}</strong>
                <p style="opacity:0.7; font-size:13px; margin:4px 0;">{summary}{date_str}</p>
                <span style="font-size:11px; opacity:0.5;">📍 {source}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button(t("选这个"), key=f"pick_{i}", use_container_width=True):
                selected = title

    if selected:
        st.session_state.analyze_topic = selected
        st.session_state.analyze_mode = "info"
        st.rerun()

    return None
