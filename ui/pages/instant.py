"""Detail page — shows analysis results. Receives topic + mode from feed page."""

import streamlit as st
from datetime import datetime

from config import is_any_llm_configured
from utils.logger import logger


def render_instant():
    """Render the detail/analysis page. Auto-runs if topic is passed in."""
    st.markdown("""
    <div style="text-align:center; margin-bottom:24px;">
        <h2>⚡ 透视分析</h2>
    </div>
    """, unsafe_allow_html=True)

    if not is_any_llm_configured():
        st.warning("⚠️ 未配置 LLM API Key，请在设置中配置后使用。搜索功能可独立使用。")

    # Get topic and mode from session state
    incoming_topic = st.session_state.pop("analyze_topic", "")
    incoming_mode = st.session_state.pop("analyze_mode", "info")

    if incoming_topic:
        # New analysis requested — store in persistent key, clear old cache
        st.session_state.current_topic = incoming_topic
        st.session_state.current_mode = incoming_mode
        st.session_state.pop("current_report", None)
        st.session_state.pop("current_summary", None)
        st.session_state.pop("current_search_results", None)
        st.session_state.pop("qa_history", None)

    topic = st.session_state.get("current_topic", "")
    mode = st.session_state.get("current_mode", "info")
    is_controversy = (mode == "controversy")

    if not topic:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; opacity:0.5;">
            <div style="font-size:64px; margin-bottom:20px;">🔍</div>
            <p style="font-size:18px;">从首页搜索或选择一条新闻开始分析</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← 返回首页", use_container_width=True):
            st.session_state.current_page = "feed"
            st.rerun()
        return

    # If report already cached, just redisplay (happens on Q&A rerun)
    cached_report = st.session_state.get("current_report")
    cached_summary = st.session_state.get("current_summary")
    cached_search = st.session_state.get("current_search_results")

    if cached_report and is_controversy:
        _display_controversy_report(topic, cached_report)
        _render_controversy_dashboard(cached_report, topic)
        _render_followup_qa(topic, cached_report, mode="controversy")
    elif cached_summary and not is_controversy:
        _display_info_result(topic, cached_summary, cached_search or [])
    elif is_controversy:
        # Fresh controversy analysis
        _run_controversy_mode(topic)
    else:
        # Fresh info analysis — disambiguate first if needed
        with st.spinner("🔍 正在分析关键词..."):
            resolved_topic = _disambiguate_topic(topic)
        if resolved_topic is None:
            return  # showing candidates, wait for user pick
        _run_info_mode(resolved_topic)

    # Back button
    st.divider()
    if st.button("← 返回首页搜索新事件", use_container_width=True):
        st.session_state.pop("current_topic", None)
        st.session_state.pop("current_mode", None)
        st.session_state.current_page = "feed"
        st.rerun()


# ============================================================
# Controversy Mode
# ============================================================

def _run_controversy_mode(topic: str):
    st.markdown(f"""
    <div style="border:1px solid rgba(128,128,128,0.15); border-radius:8px; padding:16px; margin-bottom:20px;">
        <strong>⚔️ 争议分析：</strong>{topic}
    </div>
    """, unsafe_allow_html=True)

    if not is_any_llm_configured():
        st.error("⚠️ 未配置 LLM API Key，无法运行争议分析。请在设置中配置 API Key。")
        return

    # Detailed status display
    with st.status("⚔️ 4-Agent 辩论流水线启动中...", expanded=True) as status:
        st.write("🔍 **情报官 (Scout)** — 正在从多源搜索中英文互联网信息...")
        st.write("⏳ 预计耗时 30-90 秒，请耐心等待")

        start_time = datetime.now()
        report = _run_live_analysis(topic)
        elapsed = (datetime.now() - start_time).total_seconds()

        if report is None:
            status.update(label="❌ 分析失败", state="error")
            return

        status.update(
            label=f"✅ 4-Agent 辩论完成（耗时 {elapsed:.0f} 秒）",
            state="complete",
            expanded=False,
        )
        st.write(f"🔍 **情报官** — 完成多源信息搜集")
        st.write(f"🧐 **审核员** — 完成交叉审查与利益关联分析")
        st.write(f"⚖️ **法官** — 完成贝叶斯真相概率计算")
        st.write(f"✍️ **撰稿人** — 完成结构化报告生成")

    # Cache for redisplay on Q&A rerun
    st.session_state.current_report = report
    _save_report(topic, report)

    _display_controversy_report(topic, report)
    _render_controversy_dashboard(report, topic)
    _render_followup_qa(topic, report, mode="controversy")


# ============================================================
# Info Mode
# ============================================================

def _run_info_mode(topic: str):
    st.markdown(f"""
    <div style="border:1px solid rgba(128,128,128,0.15); border-radius:8px; padding:16px; margin-bottom:20px;">
        <strong>📋 资讯梳理：</strong>{topic}
    </div>
    """, unsafe_allow_html=True)
    with st.spinner("🔍 正在搜集相关信息..."):
        search_results = _search_info(topic)

    if not search_results:
        st.warning(f"未搜索到任何结果，请尝试用更具体的关键词。")
        if st.button("← 返回首页重新搜索", use_container_width=True):
            st.session_state.pop("current_topic", None)
            st.session_state.pop("current_mode", None)
            st.session_state.current_page = "feed"
            st.rerun()
        return

    # Filter irrelevant results
    original_results = list(search_results)
    if is_any_llm_configured() and len(search_results) > 3:
        with st.spinner("🔍 正在筛选与事件相关的信息来源..."):
            search_results = _filter_relevant(topic, search_results)

    # If all filtered out, show the raw search results as candidates
    if not search_results:
        st.warning(f"搜索到的结果似乎与「{topic}」不直接相关。以下是原始搜索结果，请选择最接近的事件：")
        _show_search_candidates(original_results)
        if st.button("← 返回首页重新搜索", use_container_width=True):
            st.session_state.pop("current_topic", None)
            st.session_state.pop("current_mode", None)
            st.session_state.current_page = "feed"
            st.rerun()
        return

    with st.spinner("📝 正在梳理信息..."):
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
    st.markdown("### 📋 信息梳理结果")
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown(summary, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📎 信息来源列表"):
        for i, r in enumerate(search_results[:10]):
            title = r.get("title", "无标题")
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

    st.divider()
    st.markdown("### ⚔️ 需要深度分析？")
    st.caption("启动 4-Agent 辩论流水线，交叉验证各方说辞，计算真相概率。")
    if st.button("⚔️ 启动争议分析", type="primary", use_container_width=True):
        st.session_state.analyze_topic = topic
        st.session_state.analyze_mode = "controversy"
        st.rerun()


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
        st.error(f"搜索失败：{e}")

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

        prompt = f"""用户搜索的事件关键词：「{topic}」

以下是搜索结果，请判断每条是否与用户搜索的事件直接相关：

{items}

只回复与事件相关的条目编号（用逗号分隔，如 1,3,5）。如果都不相关，回复 NONE。"""

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
            if st.button("选这个", key=f"cand_{i}", use_container_width=True):
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

            prompt = f"""请对以下关于「{topic}」的信息进行客观梳理，生成一份新闻稿式的资讯概述。

要求：
1. 用中文，像写新闻稿一样自然叙述，不要用「开端」「发展」「争议」等死板的小标题
2. 5-8 段，内容覆盖：事件起因、经过、争议焦点、当前结果、后续影响（自然融入叙述中）
3. 每个自然段末尾用上标索引标注信息来源，如 [1]、[2]
4. 不要添加主观评价，纯资讯梳理
5. 文末附「信息来源索引」列出每个编号对应的来源名称

信息来源：
{sources_text}"""

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

def _run_live_analysis(topic: str) -> str | None:
    try:
        from agents.crew import run_analysis
        report = run_analysis(topic)
        return str(report)
    except Exception as e:
        logger.error(f"Live analysis failed: {e}")
        st.error(f"AI 分析出现错误：{str(e)}")
        return None


# ============================================================
# Persistence
# ============================================================

def _save_report(topic: str, report: str):
    try:
        import re
        from utils.persistence import save_report
        prob_match = re.search(r"真相可能概率\s*\|\s*([\d.]+)%", report)
        truth_prob = float(prob_match.group(1)) if prob_match else 50.0
        if not (0 <= truth_prob <= 100):
            truth_prob = min(max(truth_prob, 0), 100) if truth_prob > 100 else (truth_prob * 100 if truth_prob < 1 else 50.0)
        save_report(topic, report, truth_prob)
    except Exception as e:
        logger.warning(f"Failed to save report: {e}")


# ============================================================
# Embedded Dashboards
# ============================================================

def _render_controversy_dashboard(report: str, topic: str):
    import re
    from ui.components import truth_probability_gauge, sentiment_bar_chart

    prob_match = re.search(r"真相可能概率\s*\|\s*([\d.]+)%", report)
    truth_prob = float(prob_match.group(1)) if prob_match else 50.0
    if not (0 <= truth_prob <= 100):
        truth_prob = min(max(truth_prob, 0), 100) if truth_prob > 100 else (truth_prob * 100 if truth_prob < 1 else 50.0)
    ev_match = re.search(r"证据链完整度\s*\|\s*([\d.]+)\s*/\s*100", report)
    evidence_score = int(ev_match.group(1)) if ev_match else 50
    sources = len(re.findall(r"\[来源:", report))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("真相可能概率", f"{truth_prob}%")
    with col2:
        st.metric("证据链完整度", f"{evidence_score}/100")
    with col3:
        st.metric("引用来源数", str(sources))

    col_l, col_r = st.columns(2)
    with col_l:
        truth_probability_gauge(truth_prob)
    with col_r:
        sentiment_bar_chart(_extract_sentiment(report))


def _render_info_dashboard(topic: str, search_results: list[dict]):
    if not search_results:
        return
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("信息来源数", str(len(search_results)))
    with col2:
        sources = set(r.get("source", "") for r in search_results if r.get("source"))
        st.metric("独立来源", str(len(sources)))
    with col3:
        total = sum(len(r.get("content", "")) for r in search_results)
        st.metric("信息量", f"{total // 100}条")

    st.markdown("#### 来源分布")
    source_counts = {}
    for r in search_results:
        src = r.get("source", "").strip()[:30] or "(未署名)"
        source_counts[src] = source_counts.get(src, 0) + 1
    for src, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        st.markdown(f"""
        <div style="display:flex; align-items:center; margin:8px 0; gap:12px;">
            <span style="flex:1; font-size:14px;">{src}</span>
            <div style="flex:1; height:6px; border-radius:3px; background:rgba(128,128,128,0.15);">
                <div style="width:{count/len(search_results)*100}%; height:100%; border-radius:3px; background:#00bfa5;"></div>
            </div>
            <span style="font-size:13px; opacity:0.6;">{count}篇</span>
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
    return sentiment if sentiment else {"angry": 0.30, "fearful": 0.20, "neutral": 0.25, "supportive": 0.15, "sarcastic": 0.10}


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

    with st.expander("💬 追问 AI（对报告内容有疑问？点击展开对话）", expanded=False):
        st.caption("就报告中的疑点、事件细节或相关背景进行追问，AI 会结合报告内容和实时搜索为你解答。")

        # Chat history display
        for qa in st.session_state[qa_key]:
            st.markdown(f"""
            <div style="margin:8px 0; padding:8px 12px; border-radius:8px; background:rgba(0,191,165,0.06);">
                <strong>🧑 你：</strong>{qa['question']}
            </div>
            <div style="margin:4px 0 12px 16px; padding:8px 12px; border-left:3px solid #00bfa5; opacity:0.85;">
                {qa['answer']}
            </div>
            """, unsafe_allow_html=True)

        # Input — use a form to isolate submission from other buttons
        with st.form(key=f"qa_form_{qa_suffix}", clear_on_submit=True):
            col_input, col_send = st.columns([5, 1])
            with col_input:
                question = st.text_input(
                    "输入追问...",
                    placeholder="例如：这个事件的最初爆料者是谁？有权威第三方检测结果吗？",
                    label_visibility="collapsed",
                    key=input_key,
                )
            with col_send:
                submitted = st.form_submit_button("发送", use_container_width=True)

        if submitted and question.strip():
            with st.spinner("🤔 AI 正在思考（判断是否需要搜索补充信息）..."):
                need_search = _should_search(topic, report_content[:2000], question.strip())
            spinner_text = "🤔 正在搜索补充信息并生成回答..." if need_search else "🤔 正在基于现有信息生成回答..."
            with st.spinner(spinner_text):
                answer = _answer_followup(topic, report_content, question.strip(), mode, need_search=need_search)
            st.session_state[qa_key].append({"question": question.strip(), "answer": answer})
            st.rerun()


def _answer_followup(topic: str, report: str, question: str, mode: str,
                     need_search: bool = False) -> str:
    """Answer a follow-up question. Intelligently triggers search only when needed."""
    if not is_any_llm_configured():
        return "⚠️ 未配置 LLM API Key，追问功能需要在 .env 中配置 API Key 后使用。"

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

        prompt = f"""你是一个判断助手。用户刚读了关于「{topic}」的报告，现在有一个追问。

## 报告内容摘要
{report[:2000]}

## 用户追问
{question}

请判断：仅凭报告现有内容是否足以回答这个追问？
- 如果报告内容足够 → 回复 NO
- 如果报告信息不足/缺失/需要最新数据/需要验证 → 回复 YES

只回复 YES 或 NO。"""

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

        prompt = f"""你是新闻分析助手。用户刚阅读了关于「{topic}」的透视报告，现在追问。

## 报告内容
{report[:3000]}{search_note}

## 用户追问
{question}

要求：
- 简洁直接，用中文
- 优先引用报告中已有信息
- 如果补充搜索有相关信息，引用并标注"🔍 实时搜索"
- 信息不足的地方诚实说明"""

        return llm.call(messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        return f"追问处理失败：{str(e)}"


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

        decision = llm.call(messages=[{"role": "user", "content": f"""用户搜索关键词：「{topic}」

搜索结果：
{titles}

判断：以上搜索结果是否指向**完全相同的一个事件**？
- 如果所有结果都在报道同一事件（不同媒体不同角度也算同一个事件）→ 回复 SPECIFIC
- 只有当前几条结果明显是**不同的事件**时才回复 AMBIGUOUS

只回复 SPECIFIC 或 AMBIGUOUS。"""}]).strip().upper()

        if "SPECIFIC" in decision:
            return topic
    except Exception:
        return topic  # If LLM fails, proceed directly rather than blocking

    # Truly ambiguous — show candidates (should be rare now)
    st.markdown("### 🔍 你的关键词指向多个可能的事件，请选择一个：")

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

    st.info("🔍 关键词较模糊，以下是可能的事件候选，请选择一个：")
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
            if st.button("选这个", key=f"pick_{i}", use_container_width=True):
                selected = title

    if selected:
        st.session_state.analyze_topic = selected
        st.session_state.analyze_mode = "info"
        st.rerun()

    return None
