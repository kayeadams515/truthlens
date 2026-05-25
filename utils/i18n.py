"""Global i18n module for Vision Lens — Chinese/English translation.

Usage:
    from utils.i18n import t, init_language
    t("选择页面")  # → "Select Page" (if lang=en), "选择页面" (if lang=zh)
    t("当前覆盖 {count} 个站点", count=5)  # → "Currently covering 5 sites"
"""

import streamlit as st

# ============================================================
# Translation Dictionary
# ============================================================
# Key strategy:
#   - Short UI strings: Chinese text IS the key, English in "en"
#   - Long LLM prompts: Named keys like "agent.scout.goal", full zh+en
# ============================================================

_TRANSLATIONS: dict[str, dict[str, str]] = {

    # =========================================================================
    # Shared UI — Navigation, Modes, Common Labels
    # =========================================================================

    # --- Navigation ---
    "### 📋 导航": {"en": "### 📋 Navigation"},
    "选择页面": {"en": "Select Page"},
    "🏠 首页": {"en": "🏠 Home"},
    "📄 详情": {"en": "📄 Details"},

    # --- Analysis Modes ---
    "📋 资讯模式": {"en": "📋 Info Mode"},
    "⚔️ 争议模式": {"en": "⚔️ Controversy Mode"},
    "🧬 争议洞察": {"en": "🧬 Insight Mode"},
    "分析模式": {"en": "Analysis Mode"},

    # --- Common Buttons ---
    "⚙️ 设置": {"en": "⚙️ Settings"},
    "← 返回首页": {"en": "← Back to Home"},
    "← 返回首页搜索新事件": {"en": "← Back to Home & Search New"},
    "← 返回首页重新搜索": {"en": "← Back to Home & Re-search"},
    "🔍 开始透视": {"en": "🔍 Analyze"},
    "✕ 收起": {"en": "✕ Collapse"},
    "📄 查看": {"en": "📄 View"},
    "🔄 刷新": {"en": "🔄 Refresh"},

    # --- Common Status ---
    "暂无数据": {"en": "No data available"},
    "未知": {"en": "Unknown"},
    "未知事件": {"en": "Unknown Event"},
    "无标题": {"en": "Untitled"},
    "综合": {"en": "Various"},
    "未署名": {"en": "Anonymous"},

    # --- Chart / Dashboard Common ---
    "真相可能概率": {"en": "Truth Probability"},
    "证据链完整度雷达图": {"en": "Evidence Chain Completeness"},
    "评论区情绪分布": {"en": "Comment Sentiment Distribution"},
    "📐 概率计算依据": {"en": "📐 Probability Rationale"},
    "AI 估算": {"en": "AI Estimate"},
    "暂无数据": {"en": "No data"},

    # --- Language Selector ---
    "语言 / Language": {"en": "Language"},

    # =========================================================================
    # app.py — Header, Sidebar, Footer, Settings, Onboarding
    # =========================================================================

    # Header
    "Vision Lens — 穿透信息迷雾，还原事实本相": {
        "en": "Vision Lens — Cut through the information fog, reveal the truth"
    },

    # Sidebar
    "导航": {"en": "Navigation"},
    "引擎：": {"en": "Engine:"},
    "情报 LLM：": {"en": "Intel LLM:"},
    "分析 LLM：": {"en": "Analysis LLM:"},
    "搜索：": {"en": "Search:"},

    # Footer
    "AI资讯透视镜 Vision Lens v0.3.0 · 4-Agent CrewAI 辩论引擎": {
        "en": "Vision Lens v0.3.0 · 4-Agent CrewAI Debate Engine"
    },
    "分析结果仅供参考，事实性信息请以官方发布为准": {
        "en": "Analysis results are for reference only. Please refer to official sources for factual information."
    },

    # Settings Dialog
    "🌐 搜索域名": {"en": "🌐 Search Domains"},
    "🔍 情报 LLM": {"en": "🔍 Intel LLM"},
    "🧠 分析 LLM": {"en": "🧠 Analysis LLM"},
    "配置 {label} 使用的 LLM": {"en": "Configure LLM for {label}"},
    "提供商": {"en": "Provider"},
    "模型": {"en": "Model"},
    "自定义模型名称": {"en": "Custom Model Name"},
    "API Key": {"en": "API Key"},
    "Base URL（可选）": {"en": "Base URL (optional)"},
    "留空则使用默认地址": {"en": "Leave blank to use default"},

    # Settings — Search
    "搜索引擎": {"en": "Search Engine"},
    "免费 2000 次/月，在 brave.com/search/api 申请": {
        "en": "Free 2,000 queries/month. Apply at brave.com/search/api"
    },
    "需自行部署 SearXNG 实例": {"en": "Requires self-hosted SearXNG instance"},
    "DuckDuckGo 免费使用，无需 API Key。可能被限速。": {
        "en": "DuckDuckGo is free, no API Key needed. May be rate-limited."
    },
    "域名过滤（Tavily / Brave / SerpAPI 支持按域名搜索，DDGS / SearXNG 不支持）": {
        "en": "Domain Filter (Tavily / Brave / SerpAPI support domain filtering; DDGS / SearXNG do not)"
    },
    "全量搜索（不限制域名）": {"en": "Search all domains (unrestricted)"},
    "当前覆盖 {count} 个站点": {"en": "Currently covering {count} sites"},
    "重置搜索域名为默认": {"en": "Reset Search Domains to Default"},
    "🧪 测试搜索": {"en": "🧪 Test Search"},
    "正在测试搜索连接...": {"en": "Testing search connection..."},

    # Settings — LLM Tabs
    "情报 LLM 用于情报官 (Scout) Agent 的信息搜集、相关性过滤与话题消歧。": {
        "en": "Intel LLM is used by the Scout Agent for information gathering, relevance filtering, and topic disambiguation."
    },
    "🧪 测试连接": {"en": "🧪 Test Connection"},
    "正在测试情报 LLM 连接...": {"en": "Testing Intel LLM connection..."},
    "分析 LLM 用于审核员、法官、撰稿人 Agent 以及资讯梳理、追问回答。": {
        "en": "Analysis LLM is used by the Challenger, Judge, Editor Agents and for info summaries and Q&A."
    },
    "正在测试分析 LLM 连接...": {"en": "Testing Analysis LLM connection..."},

    # Settings — Bottom
    "🧪 测试全部": {"en": "🧪 Test All"},
    "正在测试全部连接...": {"en": "Testing all connections..."},
    "💾 保存设置": {"en": "💾 Save Settings"},
    "设置已保存": {"en": "Settings saved"},
    "切换厂商时自动缓存已配置的 API Key / URL，切回无需重输。": {
        "en": "API Key / URL are auto-cached when switching providers — no need to re-enter when switching back."
    },
    "⬜ 未测试": {"en": "⬜ Not tested"},
    "✅ 连接可用": {"en": "✅ Connected"},
    "未配置 API Key": {"en": "API Key not configured"},
    "可用": {"en": "Available"},
    "返回为空": {"en": "Empty response"},
    "搜索无结果": {"en": "No search results"},

    # Domain Names (used in domain checkboxes)
    "🇨🇳 官方媒体": {"en": "🇨🇳 Official Media"},
    "🇨🇳 门户资讯": {"en": "🇨🇳 Portal & News"},
    "🇨🇳 社交平台": {"en": "🇨🇳 Social Platforms"},
    "🌍 国际媒体": {"en": "🌍 International Media"},
    "🌍 社交平台": {"en": "🌍 Social Platforms"},

    # Onboarding
    "👋 欢迎使用 AI资讯透视镜": {"en": "👋 Welcome to Vision Lens"},
    "⚙️ 打开设置": {"en": "⚙️ Open Settings"},
    "🔍 先看看（模拟演示）": {"en": "🔍 Preview (Demo)"},

    # Test status
    "情报": {"en": "Intel"},
    "分析": {"en": "Analysis"},

    # =========================================================================
    # ui/pages/feed.py — Discovery Feed
    # =========================================================================

    "📡 发现·透视报告": {"en": "📡 Discovery & Reports"},
    "搜索新闻 · 本周热点 · 历史报告": {
        "en": "Search News · Weekly Hot · History"
    },
    "🔍 输入你想透视的新闻事件": {"en": "🔍 Enter a news event to analyze"},
    "输入新闻关键词或粘贴链接...": {"en": "Enter keywords or paste a link..."},

    # Mode captions
    "🧬 争议洞察：社交媒体舆论阵营深度分析，适合吃瓜、八卦、热门话题。约 20-40 秒。": {
        "en": "🧬 Insight: Deep analysis of social media opinion camps. For controversies, gossip, trending topics. ~20-40s."
    },
    "⚔️ 争议模式：4-Agent 辩论流水线，深度交叉验证各方说辞，计算真相概率。约 30-90 秒。": {
        "en": "⚔️ Controversy: 4-Agent debate pipeline. Cross-verify claims and calculate truth probability. ~30-90s."
    },
    "📋 资讯模式：快速搜集和梳理信息，展示事件全貌。": {
        "en": "📋 Info: Quick information gathering and summarization. Shows the full picture."
    },

    # Weekly News
    "🇨🇳 中国热点": {"en": "🇨🇳 China Hot Topics"},
    "🌍 全球热点": {"en": "🌍 Global Hot Topics"},
    "🔍 正在搜索本周热点新闻...": {"en": "🔍 Searching for this week's hot news..."},

    # History
    "### 📋 历史透视报告": {"en": "### 📋 Analysis History"},
    "已分析 · {generated}": {"en": "Analyzed · {generated}"},
    "### 📊 数据透视": {"en": "### 📊 Data Dashboard"},
    "图表加载失败": {"en": "Chart failed to load"},
    "渲染卡片失败": {"en": "Card render failed"},

    # News Cards
    "🔍 分析此事件": {"en": "🔍 Analyze"},
    "📋 资讯模式": {"en": "📋 Info Mode"},
    "⚔️ 争议模式": {"en": "⚔️ Controversy Mode"},

    # Locations (used in news card display)
    "香港": {"en": "Hong Kong"},
    "北京": {"en": "Beijing"},
    "上海": {"en": "Shanghai"},
    "深圳": {"en": "Shenzhen"},
    "广州": {"en": "Guangzhou"},
    "台湾": {"en": "Taiwan"},
    "美国": {"en": "USA"},
    "英国": {"en": "UK"},
    "日本": {"en": "Japan"},
    "韩国": {"en": "South Korea"},
    "法国": {"en": "France"},
    "德国": {"en": "Germany"},
    "印度": {"en": "India"},
    "俄罗斯": {"en": "Russia"},
    "乌克兰": {"en": "Ukraine"},
    "中东": {"en": "Middle East"},
    "欧盟": {"en": "EU"},

    # =========================================================================
    # ui/pages/instant.py — Analysis Page
    # =========================================================================

    # Page header
    "⚡ 透视分析": {"en": "⚡ Analysis"},
    "⚠️ 未配置 LLM API Key，请在设置中配置后使用。搜索功能可独立使用。": {
        "en": "⚠️ LLM API Key not configured. Please configure in Settings. Search can still be used independently."
    },
    "从首页搜索或选择一条新闻开始分析": {
        "en": "Search or select a news item from the Home page to start analysis"
    },

    # Info mode
    "📋 资讯梳理：": {"en": "📋 Info Summary:"},
    "🔍 正在分析关键词...": {"en": "🔍 Analyzing keywords..."},
    "🔍 正在搜集相关信息...": {"en": "🔍 Gathering information..."},
    "📝 正在梳理信息...": {"en": "📝 Summarizing information..."},
    "🔍 正在筛选与事件相关的信息来源...": {"en": "🔍 Filtering relevant sources..."},
    "未搜索到任何结果，请尝试用更具体的关键词。": {
        "en": "No results found. Try more specific keywords."
    },
    "搜索到的结果似乎与「{topic}」不直接相关。以下是原始搜索结果，请选择最接近的事件：": {
        "en": "Results don't seem directly related to「{topic}」. Here are the raw results — pick the closest match:"
    },
    "### 📋 信息梳理结果": {"en": "### 📋 Info Summary"},
    "📎 信息来源列表": {"en": "📎 Source List"},
    "### ⚔️ 需要深度分析？": {"en": "### ⚔️ Need Deeper Analysis?"},
    "启动 4-Agent 辩论流水线，交叉验证各方说辞，计算真相概率。": {
        "en": "Launch the 4-Agent debate pipeline to cross-verify claims and calculate truth probability."
    },
    "⚔️ 启动争议分析": {"en": "⚔️ Launch Controversy Analysis"},
    "搜索失败：": {"en": "Search failed: "},

    # Controversy mode
    "⚔️ 争议分析：": {"en": "⚔️ Controversy Analysis:"},
    "⚠️ 未配置 LLM API Key，无法运行争议分析。请在设置中配置 API Key。": {
        "en": "⚠️ LLM API Key not configured. Cannot run controversy analysis. Please configure in Settings."
    },
    "⚔️ 4-Agent 辩论流水线启动中...": {"en": "⚔️ 4-Agent Debate Pipeline starting..."},
    "🔍 **情报官 (Scout)** — 正在从多源搜索中英文互联网信息...": {
        "en": "🔍 **Scout** — Gathering multi-source intel from Chinese and English web..."
    },
    "⏳ 预计耗时 30-90 秒，请耐心等待": {
        "en": "⏳ Estimated 30-90 seconds, please wait..."
    },
    "❌ 分析失败": {"en": "❌ Analysis failed"},
    "✅ 4-Agent 辩论完成（耗时 {elapsed:.0f} 秒）": {
        "en": "✅ 4-Agent Debate complete ({elapsed:.0f}s)"
    },
    "🔍 **情报官** — 完成多源信息搜集": {
        "en": "🔍 **Scout** — Multi-source intelligence gathering complete"
    },
    "🧐 **审核员** — 完成交叉审查与利益关联分析": {
        "en": "🧐 **Challenger** — Cross-examination and interest analysis complete"
    },
    "⚖️ **法官** — 完成贝叶斯真相概率计算": {
        "en": "⚖️ **Judge** — Bayesian truth probability calculation complete"
    },
    "✍️ **撰稿人** — 完成结构化报告生成": {
        "en": "✍️ **Editor** — Structured report generation complete"
    },
    "AI 分析出现错误：": {"en": "AI analysis error: "},

    # Insight mode
    "🧬 争议洞察：": {"en": "🧬 Controversy Insight:"},
    "⚠️ 未配置 LLM API Key。争议洞察需要 LLM 进行深度分析。将使用模板化输出。": {
        "en": "⚠️ LLM API Key not configured. Insight mode needs LLM for deep analysis. Using template output."
    },
    "🔍 正在搜集社交媒体讨论...": {"en": "🔍 Gathering social media discussions..."},
    "未找到关于「{topic}」的社交媒体讨论，请尝试换一个关键词或更宽泛的表述。": {
        "en": "No social media discussions found for「{topic}」. Try a different keyword or broader phrasing."
    },
    "💡 提示：确保已在设置中配置搜索 API Key（如 Tavily），或尝试切换到 DuckDuckGo。": {
        "en": "💡 Tip: Make sure a search API Key is configured in Settings (e.g. Tavily), or try switching to DuckDuckGo."
    },
    "✅ 搜集到 {count} 条相关讨论": {"en": "✅ Found {count} relevant discussions"},
    "🧐 正在识别舆论阵营与情绪分布...": {
        "en": "🧐 Identifying opinion camps and sentiment distribution..."
    },
    "✅ 识别出 {num} 个舆论阵营：{names}": {
        "en": "✅ Identified {num} opinion camps: {names}"
    },
    "ℹ️ 未能清晰识别舆论阵营，将生成通用报告": {
        "en": "ℹ️ Could not clearly identify opinion camps — generating general report"
    },
    "👥 涉及 {num} 个圈层/社区": {"en": "👥 Involving {num} communities/circles"},
    "✍️ 正在撰写洞察报告...": {"en": "✍️ Writing insight report..."},
    "⏱️ 耗时 {elapsed:.0f} 秒": {"en": "⏱️ Completed in {elapsed:.0f}s"},
    "❌ 争议洞察分析出错：": {"en": "❌ Insight analysis error: "},
    "请检查网络连接和 API 配置后重试。": {
        "en": "Please check network connection and API configuration."
    },

    # Insight Dashboard
    "### 📊 争议洞察仪表盘": {"en": "### 📊 Controversy Insight Dashboard"},
    "⚠️ 以下数值为 AI 基于搜索结果的**定性估算**，非精确统计数据，仅供参考舆论格局": {
        "en": "⚠️ Values below are AI **qualitative estimates** based on search results — not precise statistics. For reference only."
    },
    "舆论阵营": {"en": "Opinion Camps"},
    " 个": {"en": ""},
    "涉及圈层": {"en": "Communities"},
    "关键节点": {"en": "Key Events"},
    "争议类型": {"en": "Type"},
    "待分析": {"en": "Pending"},
    "🧬 已识别为梗/网络流行语类话题 — 报告包含梗百科溯源": {
        "en": "🧬 Identified as meme/internet slang topic — report includes meme origin tracing"
    },
    "舆论阵营规模分布": {"en": "Opinion Camp Distribution"},
    "舆论阵营规模分布（AI 估算）": {"en": "Opinion Camp Distribution (AI Estimate)"},
    "估计占比 (%)": {"en": "Est. Share (%)"},
    "阵营占比由 AI 估算，不代表精确统计数据": {
        "en": "Camp shares are AI estimates, not precise statistics"
    },
    "情绪分布": {"en": "Sentiment Distribution"},
    "跨平台情绪对比（AI 估算）": {"en": "Cross-Platform Sentiment (AI Estimate)"},
    "跨平台情绪对比": {"en": "Cross-Platform Sentiment"},
    "🏷️ 争议基因：": {"en": "🏷️ Controversy Genes:"},
    "📖 基因标签解读": {"en": "📖 Gene Tag Explanation"},
    "#### 🔄 观点迁移": {"en": "#### 🔄 Opinion Shifts"},
    "#### 🧠 深层矛盾洞察": {"en": "#### 🧠 Underlying Tensions"},
    "#### 🎯 圈层视角": {"en": "#### 🎯 Community Perspectives"},
    "圈层": {"en": "Community"},
    "独特视角": {"en": "Perspective"},
    "倾向阵营": {"en": "Leans Toward"},
    "争议演变时间线（AI 梳理）": {"en": "Controversy Timeline (AI Reconstructed)"},
    "热度": {"en": "Heat"},
    "🔴 引爆点  🟠 反转  🔵 升级  🟢 平息": {
        "en": "🔴 Trigger  🟠 Reversal  🔵 Escalation  🟢 Resolution"
    },
    "### ⚔️ 需要更深度的事实核查？": {"en": "### ⚔️ Need Deeper Fact-Checking?"},
    "启动 4-Agent 辩论流水线，交叉验证各方说辞，计算真相概率。适合需要核实事实的争议事件。": {
        "en": "Launch the 4-Agent debate pipeline to cross-verify claims and calculate truth probability. Suitable for events needing fact verification."
    },

    # Info Dashboard
    "信息来源数": {"en": "Sources"},
    "独立来源": {"en": "Unique Sources"},
    "信息量": {"en": "Info Volume"},
    "条": {"en": "items"},
    "#### 来源分布": {"en": "#### Source Distribution"},
    "篇": {"en": " articles"},

    # Controversy Dashboard
    "引用来源数": {"en": "Citations"},
    "证据链完整度": {"en": "Evidence Score"},

    # Follow-up Q&A
    "💬 追问 AI（对报告内容有疑问？点击展开对话）": {
        "en": "💬 Ask AI (Have questions about the report? Click to expand)"
    },
    "就报告中的疑点、事件细节或相关背景进行追问，AI 会结合报告内容和实时搜索为你解答。": {
        "en": "Ask about unclear points in the report, event details, or background. AI will answer using the report and live search."
    },
    "输入追问...": {"en": "Type your question..."},
    "例如：这个事件的最初爆料者是谁？有权威第三方检测结果吗？": {
        "en": "e.g. Who first reported this? Are there third-party test results?"
    },
    "发送": {"en": "Send"},
    "🤔 AI 正在思考（判断是否需要搜索补充信息）...": {
        "en": "🤔 AI is thinking (deciding if search is needed)..."
    },
    "🤔 正在搜索补充信息并生成回答...": {
        "en": "🤔 Searching for supplementary info and generating answer..."
    },
    "🤔 正在基于现有信息生成回答...": {
        "en": "🤔 Generating answer based on existing information..."
    },

    # Q&A messages
    "🧑 你：": {"en": "🧑 You: "},
    "⚠️ 未配置 LLM API Key，追问功能需要在 .env 中配置 API Key 后使用。": {
        "en": "⚠️ LLM API Key not configured. Q&A requires API Key configuration."
    },

    # Disambiguation
    "🔍 你的关键词指向多个可能的事件，请选择一个：": {
        "en": "🔍 Your keyword matches multiple possible events. Please select one:"
    },
    "🔍 关键词较模糊，以下是可能的事件候选，请选择一个：": {
        "en": "🔍 Vague keyword — here are possible matches. Please select one:"
    },
    "选这个": {"en": "Select"},

    # Source info panel
    "争议洞察 | {model_short}": {"en": "Controversy Insight | {model_short}"},
    "Live AI": {"en": "Live AI"},
    "未配置 LLM": {"en": "No LLM"},

    # =========================================================================
    # ui/components.py — Chart Components
    # =========================================================================

    # sentiment_bar_chart labels
    "愤怒 😡": {"en": "Angry 😡"},
    "恐惧 😨": {"en": "Fear 😨"},
    "中立 😐": {"en": "Neutral 😐"},
    "支持 👍": {"en": "Support 👍"},
    "同情 🤝": {"en": "Sympathy 🤝"},
    "讽刺 😏": {"en": "Sarcasm 😏"},

    # =========================================================================
    # agents/scout.py — Scout Agent
    # =========================================================================

    "agent.scout.role": {
        "zh": "情报官 (Scout)",
        "en": "Intelligence Officer (Scout)",
    },
    "agent.scout.goal": {
        "zh": (
            "针对用户输入的事件话题，从多个维度全面搜集信息："
            "1) 官方/权威机构的通报与声明；"
            "2) 自媒体/KOL的观点及爆料；"
            "3) 社交媒体(微博、抖音、知乎)上代表性评论及其情绪色彩；"
            "4) 事件关键时间线与参与方的利益关系网络。"
            "最终输出一份结构化的原始情报汇编，供下游Agent分析使用。"
        ),
        "en": (
            "Gather multi-source intelligence on the user's topic from these dimensions:\n"
            "1) Official/authoritative announcements and statements;\n"
            "2) Independent media/KOL opinions and revelations;\n"
            "3) Representative social media comments and their emotional tone;\n"
            "4) Event timeline and stakeholder interest networks.\n"
            "Output a structured intelligence dossier for downstream agents."
        ),
    },
    "agent.scout.backstory": {
        "zh": (
            "你是一位经验丰富的情报分析师，曾在国家级媒体担任调查记者15年。"
            "你精通OSINT(开源情报)技术，能从海量碎片信息中提炼关键事实。"
            "你深知：真相往往藏在细节中，而每一方的说辞都带着各自的立场和动机。"
            "你的职业信条是：不放过任何一条线索，不给任何一方特殊待遇。"
        ),
        "en": (
            "You are an experienced intelligence analyst and former investigative journalist "
            "with 15 years at a national media outlet. You excel at OSINT techniques and "
            "extracting key facts from fragmented information. You know that truth hides in "
            "the details and every party speaks from their own position and motives. "
            "Your creed: leave no lead unfollowed, give no party special treatment."
        ),
    },

    # =========================================================================
    # agents/challenger.py — Challenger Agent
    # =========================================================================

    "agent.challenger.role": {
        "zh": "杠精审核员 (Challenger)",
        "en": "Adversarial Reviewer (Challenger)",
    },
    "agent.challenger.goal": {
        "zh": (
            "对情报官搜集的原始情报进行无死角的交叉审查。你必须做到：\n"
            "1) **交叉比对证据**：将不同来源的信息进行时空、逻辑上的比对，标记出互相印证或互相矛盾之处；\n"
            "2) **挖掘利益关联**：分析每一条观点背后可能的利益动机——是纯粹的公共关切？还是厂商公关？竞争对手抹黑？流量变现？\n"
            "3) **寻找逻辑漏洞**：指出论证中的逻辑谬误(如稻草人、虚假两难、以偏概全、诉诸情感、因果倒置等)；\n"
            "4) **识别水军/公关痕迹**：通过语言模式分析，标记疑似有组织的信息操控行为(如短时间大量相似话术、异常的情绪极端化等)；\n"
            "5) **检测反讽与弦外之音**：识别评论中的讽刺、阴阳怪气、高级黑等隐性表达。\n\n"
            "输出格式：针对每一方观点，给出【可信度评估】【利益相关度分析】【逻辑漏洞清单】【信息交叉验证结果】。"
        ),
        "en": (
            "Conduct thorough adversarial cross-examination of the Scout's intelligence. You must:\n"
            "1) **Cross-verify evidence**: Compare information across sources in time, space, and logic — mark corroborations and contradictions;\n"
            "2) **Map interest networks**: Analyze the motivations behind each viewpoint — public concern? Corporate PR? Competitor smears? Monetization?\n"
            "3) **Find logical fallacies**: Identify reasoning flaws (strawman, false dilemma, hasty generalization, appeal to emotion, reverse causality, etc.);\n"
            "4) **Detect bot/PR patterns**: Flag signs of coordinated information manipulation through linguistic pattern analysis;\n"
            "5) **Read between the lines**: Detect sarcasm, passive-aggression, and veiled expressions.\n\n"
            "Output: For each viewpoint — [Credibility Assessment] [Interest Analysis] [Logical Fallacies] [Cross-verification Results]."
        ),
    },
    "agent.challenger.backstory": {
        "zh": (
            "你是一位著名的'事实核查员'和'辩论终结者'。在圈内以'杠精'著称——"
            "不是因为你不讲道理，而是因为你从不接受任何未经严格检验的论断。"
            "你曾在国际事实核查网络(IFCN)工作，审查过上千条争议性新闻，揭穿过数十起大规模舆论操控事件。"
            "你的口头禅是：'如果一件事听起来太过完美，那它大概率是假的。如果一件事听起来太过荒谬，那它大概率被断章取义了。'"
            "你对人性有深刻的理解：利益在哪里，谎言就在哪里。"
        ),
        "en": (
            "You are a renowned fact-checker and debate-terminator. Known as a 'skeptic' — "
            "not because you are unreasonable, but because you never accept unverified claims. "
            "You worked at the International Fact-Checking Network (IFCN), reviewing thousands of "
            "controversial stories and exposing dozens of large-scale information manipulation campaigns. "
            "Your motto: 'If it sounds too perfect, it's probably false. If it sounds too absurd, "
            "it's probably taken out of context.' You understand human nature deeply: "
            "where there is interest, there are lies."
        ),
    },

    # =========================================================================
    # agents/judge.py — Judge Agent
    # =========================================================================

    "agent.judge.role": {
        "zh": "理性法官 (Judge)",
        "en": "Rational Judge",
    },
    "agent.judge.goal": {
        "zh": (
            "基于逻辑学和贝叶斯推断框架，对事件的各方主张进行理性裁决。你的职责：\n\n"
            "1) **证据链完整性评分**：对每一个核心主张，评估其证据链的完整性(0-100%)。"
            "考虑因素包括：直接证据 vs 间接证据、一手来源 vs N手转载、可验证性、时序一致性；\n"
            "2) **贝叶斯概率计算**：综合所有证据，计算'核心主张为真'的后验概率。"
            "你需要明确给出先验概率(基于常识)、似然比(证据的证明力)，以及最终的后验概率；\n"
            "3) **缺失证据清单**：明确指出如果要确证或证伪某个主张，还需要哪些关键证据，"
            "以及这些证据应该从何处获取；\n"
            "4) **剥离情绪噪音**：将事实陈述与情绪表达分离，不因情绪强烈程度影响证据判断。\n\n"
            "重要原则：\n"
            "- 不能证实 ≠ 不能证伪。对无法验证的主张标注'待证实'而非'假'。\n"
            "- 相关性 ≠ 因果性。严格区分两者。\n"
            "- 证据的缺失 ≠ 缺失的证据。不要因为缺少反证就默认主张为真。"
        ),
        "en": (
            "Apply logical reasoning and Bayesian inference to evaluate all claims in the event. Your duties:\n\n"
            "1) **Evidence Chain Scoring**: For each core claim, rate evidence completeness (0-100%). "
            "Consider: direct vs. circumstantial evidence, primary vs. secondary sources, verifiability, temporal consistency;\n"
            "2) **Bayesian Probability**: Synthesize all evidence to compute the posterior probability of the core claim. "
            "Explicitly state the prior probability (based on common sense), likelihood ratios (evidential weight), and final posterior;\n"
            "3) **Missing Evidence List**: Identify what key evidence is still needed to confirm or refute each claim, "
            "and where to obtain it;\n"
            "4) **Strip Emotional Noise**: Separate factual statements from emotional expressions. "
            "Do not let emotional intensity affect evidence evaluation.\n\n"
            "Key principles:\n"
            "- Cannot prove ≠ Can disprove. Label unverifiable claims as 'Unverified', not 'False'.\n"
            "- Correlation ≠ Causation. Strictly distinguish the two.\n"
            "- Absence of evidence ≠ Evidence of absence. Do not default to true when counter-evidence is missing."
        ),
    },
    "agent.judge.backstory": {
        "zh": (
            "你是一位精通逻辑学和概率论的退休高级法官。在30年的法官生涯中，"
            "你审理过2000多起案件，形成了自己独特的'贝叶斯裁判法'——"
            "从不凭直觉断案，每一步判断都基于先验概率和证据似然比的计算。"
            "退休后你专注于研究信息时代的真相判定问题，发表了《后真相时代的证据法》一书。"
            "你深知：人类的情感是真相最大的敌人。愤怒的时候，人会把1%的可能性当成99%。"
            "恐惧的时候，人会把99%的安全当成1%。你的任务就是纠正这些认知偏差。"
        ),
        "en": (
            "You are a retired senior judge with expertise in logic and probability theory. "
            "Over 30 years on the bench, you presided over 2,000+ cases and developed your unique "
            "'Bayesian Adjudication Method' — never relying on intuition, always grounding every "
            "decision in prior probability and likelihood ratio calculations. "
            "In retirement, you wrote 'Evidence Law in the Post-Truth Era'. "
            "You know that human emotion is truth's greatest enemy. In anger, people mistake "
            "a 1% chance for 99%. In fear, they mistake 99% safety for 1%. "
            "Your mission is to correct these cognitive biases."
        ),
    },

    # =========================================================================
    # agents/editor.py — Editor Agent
    # =========================================================================

    "agent.editor.role": {
        "zh": "首席撰稿人 (Editor)",
        "en": "Chief Editor",
    },
    "agent.editor.goal": {
        "zh": (
            "将情报官、审核员、法官的分析成果整合为一份结构化、完全客观的新闻透视报告。"
            "你必须严格遵循以下输出规范：\n\n"
            "## 报告结构（必须严格遵循）\n\n"
            "### 📌 事件概述\n"
            "- 像写新闻稿一样自然地叙述事件，不要用「开端」「发展」「争议」等小标题\n"
            "- 内容上要覆盖：事件起因 → 经过 → 争议焦点 → 当前结果 → 后续影响，但融合在流畅的段落中\n"
            "- 3-5 段，段与段之间逻辑连贯，读完就能全面了解事件\n"
            "- **禁止使用任何主观修饰词**（如'令人震惊''不幸''骇人听闻'等）\n"
            "- 每个自然段末尾用上标索引标注信息来源，如 [1]、[2]\n\n"
            "### 📊 真相透视表\n"
            "- **本表评估的核心主张**：[从法官报告中提取，如'XX品牌汽车存在设计缺陷']\n"
            "- **真相可能概率**：该主张为真的后验概率（XX%）\n"
            "- **概率计算依据**：法官Agent的贝叶斯推理过程简述\n"
            "- **证据链完整度**: XX/100\n"
            "- **缺失的关键证据**: 列举3-5项\n\n"
            "### ⚖️ 各方观点对垒\n"
            "- **首先用一段话总结各方主要观点和举证内容**，让读者快速了解争议的焦点和各方的核心论据\n"
            "#### 🏛️ 官方/权威方\n"
            "- 核心说辞 + 支撑证据 + 置信度评分\n"
            "- 如有逻辑漏洞，一并列出\n"
            "- 如有原文URL，在段末用 [来源N](url) 格式标注\n\n"
            "#### 📢 自媒体/KOL方\n"
            "- 核心说辞 + 利益相关度分析 + 逻辑漏洞\n"
            "- 区分不同自媒体的立场差异\n"
            "- 如有原文URL，用 [来源N](url) 格式\n\n"
            "#### 💬 评论区舆情\n"
            "- **首先用一段话总结评论区主要情绪倾向和核心观点**\n"
            "- 情绪分布统计（可量化表达的占比）\n"
            "- 代表性神评分析（挑选2-3条高质量评论，每条简述其洞察价值）\n"
            "- 反转信号检测\n\n"
            "### 🔍 事实链条对齐\n"
            "- ✅ 已确认事实（多方交叉验证通过）\n"
            "- ⚠️ 存疑点（证据不足或来源单一）\n"
            "- ❌ 矛盾点（各方说法存在直接冲突）\n\n"
            "### 📎 信息来源索引\n"
            "- 列出所有引用的来源编号及对应的来源名称/URL\n\n"
            "## 引用格式规范\n"
            "1. 文中引用：在每个自然段末尾用上标索引 [1]、[2]、[3]\n"
            "2. 原文链接：用 Markdown 链接语法 [来源名称](url)，让链接文字为来源名称，而非裸露URL\n"
            "3. 文末必须有「信息来源索引」汇总所有引用\n"
            "4. 同一来源多次引用时使用同一编号\n\n"
            "## 关键规则\n"
            "1. **绝不编造数据**：所有数字、百分比、事实陈述必须来自上游Agent的输出\n"
            "2. **区分事实与观点**：明确标注哪部分是'事实陈述'，哪部分是'观点推断'\n"
            "3. **不确定性诚实表达**：不知道就说不知道，证据不足就标注证据不足"
        ),
        "en": (
            "Integrate analysis from the Scout, Challenger, and Judge into a structured, "
            "fully objective news analysis report. Strictly follow this output specification:\n\n"
            "## Report Structure (must follow strictly)\n\n"
            "### 📌 Event Overview\n"
            "- Narrate the event naturally like a news article — no rigid sub-headers like 'Beginning' or 'Development'\n"
            "- Cover: cause → progression → controversy → current outcome → aftermath — woven into flowing paragraphs\n"
            "- 3-5 paragraphs with logical flow, providing a comprehensive picture\n"
            "- **No subjective modifiers** (e.g., 'shocking', 'tragic', 'appalling')\n"
            "- End each paragraph with superscript source citations like [1], [2]\n\n"
            "### 📊 Truth Dashboard\n"
            "- **Core Claim Under Review**: [Extracted from Judge's report, e.g. 'Brand X vehicle has a design defect']\n"
            "- **Truth Probability**: Posterior probability the claim is true (XX%)\n"
            "- **Probability Rationale**: Summary of Judge's Bayesian reasoning\n"
            "- **Evidence Chain Completeness**: XX/100\n"
            "- **Missing Key Evidence**: List 3-5 items\n\n"
            "### ⚖️ Viewpoint Showdown\n"
            "- **Open with a paragraph summarizing all sides' main arguments and evidence**\n"
            "#### 🏛️ Official/Authority Side\n"
            "- Core narrative + supporting evidence + confidence score\n"
            "- List any logical fallacies found\n"
            "- Cite original URLs using [Source N](url) format\n\n"
            "#### 📢 Independent Media/KOL Side\n"
            "- Core narrative + interest analysis + logical fallacies\n"
            "- Distinguish between different KOLs' positions\n"
            "- Cite original URLs using [Source N](url) format\n\n"
            "#### 💬 Public Sentiment\n"
            "- **Open with a paragraph summarizing overall sentiment and key opinions**\n"
            "- Sentiment distribution statistics (quantifiable ratios)\n"
            "- Notable comment analysis (pick 2-3 high-quality comments, note their insight value)\n"
            "- Reversal signal detection\n\n"
            "### 🔍 Fact Alignment\n"
            "- ✅ Confirmed Facts (cross-verified by multiple sources)\n"
            "- ⚠️ Uncertain Points (insufficient evidence or single source)\n"
            "- ❌ Contradictions (direct conflicts between sources)\n\n"
            "### 📎 Source Index\n"
            "- List all cited source numbers with corresponding source name/URL\n\n"
            "## Citation Format\n"
            "1. In-text: Superscript indices [1], [2], [3] at paragraph end\n"
            "2. Links: Use Markdown [source name](url) — show source name, not bare URL\n"
            "3. Must include a 'Source Index' at the end\n"
            "4. Same source cited multiple times uses the same number\n\n"
            "## Key Rules\n"
            "1. **Never fabricate data**: All numbers, percentages, and factual claims must come from upstream agents\n"
            "2. **Distinguish fact from opinion**: Clearly label what is 'factual' vs. 'opinion/inference'\n"
            "3. **Honest uncertainty**: Say you don't know when you don't know; mark insufficient evidence clearly"
        ),
    },
    "agent.editor.backstory": {
        "zh": (
            "你是一位从业20年的资深编辑，曾在路透社和财新传媒担任高级编辑，"
            "以'冷峻客观、一字不苟'的文风著称。你经手的每一篇报道都经得起最严格的核查。"
            "你的职业准则：事实就是事实，观点就是观点，两者之间的界限比你家的门禁还严格。"
            "你最痛恨的两件事：1) 在报道中夹带私货 2) 把推测当事实。"
            "你采用学术论文的引用规范来撰写新闻报道——每个自然段末尾标注上标索引，文末附来源汇总。"
            "链接文字为来源名称，而非裸露URL，视觉干净利落。"
        ),
        "en": (
            "You are a veteran editor with 20 years of experience, formerly a senior editor "
            "at Reuters and Caixin. Known for your cold objectivity and meticulous precision, "
            "every piece you've edited can withstand the strictest scrutiny. "
            "Your professional code: facts are facts, opinions are opinions — the boundary "
            "between them is stricter than your front door. "
            "You despise two things: 1) smuggling bias into reporting 2) passing speculation as fact. "
            "You apply academic citation standards to news reporting — superscript indices at "
            "paragraph ends, with a source index at the bottom. Link text shows source names, "
            "not bare URLs — clean and professional."
        ),
    },

    # =========================================================================
    # agents/crew.py — Crew Task Descriptions
    # =========================================================================

    "task.crew.scout": {
        "zh": (
            "用户关注的事件话题是：「{topic}」\n\n"
            "请使用你的搜索工具，从以下维度全面搜集信息：\n"
            "1. 使用搜索工具搜索该话题，获取官方通报、媒体报道、社交媒体讨论\n"
            "2. 提取事件关键时间线上的每一个节点\n"
            "3. 识别事件中的各利益相关方及其公开立场\n"
            "4. 选取社交媒体上最具代表性的评论(包括不同情绪倾向的)\n\n"
            "输出要求：用中文输出结构化的情报汇编，包含：\n"
            "- 事件5W1H基本信息\n"
            "- 官方/权威方声明(逐条列出，注明出处)\n"
            "- 自媒体/KOL观点(逐条列出，注明发布者、粉丝量、可能的利益关联)\n"
            "- 社交媒体代表性评论(至少5条，注明情绪倾向和点赞量)\n"
            "- 情绪分布统计(给出各情绪的大致占比)\n\n"
            "如果有URL链接注明原始链接。所有信息必须标注来源。"
        ),
        "en": (
            "The user is interested in the event: 「{topic}」\n\n"
            "Use your search tools to gather comprehensive intelligence:\n"
            "1. Search the topic for official statements, media reports, social media discussions\n"
            "2. Extract every node on the event's key timeline\n"
            "3. Identify all stakeholders and their public positions\n"
            "4. Select the most representative social media comments (across emotional tones)\n\n"
            "Output: A structured intelligence dossier in English containing:\n"
            "- Event 5W1H basics\n"
            "- Official/authoritative statements (list individually, cite sources)\n"
            "- Independent media/KOL viewpoints (list individually, note publisher, follower count, potential interests)\n"
            "- Representative social media comments (at least 5, note emotional tone and engagement)\n"
            "- Sentiment distribution (approximate ratio of each sentiment)\n\n"
            "Include original URLs where available. All information must cite sources."
        ),
    },
    "task.crew.scout.expected": {
        "zh": (
            "一份结构化的原始情报汇编，包含5W1H信息、官方声明列表、自媒体观点列表、"
            "社交媒体代表性评论、情绪分布统计。所有条目必须标注来源。"
        ),
        "en": (
            "A structured intelligence dossier containing 5W1H info, official statement list, "
            "independent media viewpoint list, representative social media comments, and sentiment "
            "distribution statistics. All entries must cite sources."
        ),
    },

    "task.crew.challenger": {
        "zh": (
            "情报官已经搜集了关于该事件的原始情报。现在请你发挥'杠精'本色，"
            "对每一条信息进行无情的交叉审查：\n\n"
            "**审查维度：**\n"
            "1. **信息一致性交叉验证**：将不同来源对同一事实的描述进行比对，标记一致/不一致/无法验证。\n"
            "2. **利益关联图绘制**：分析每一个发言方背后可能的经济、政治或流量利益。谁是受益者？谁是受害者？\n"
            "3. **逻辑谬误诊断**：逐一检查各方论证中的逻辑漏洞(稻草人、假两难、滑坡、诉诸情感、以偏概全等)。\n"
            "4. **水军/异常行为检测**：是否存在短时间内大量相似话术？是否存在与正常讨论模式不符的情绪极端化？\n"
            "5. **反讽与潜台词解读**：识别阴阳怪气、高级黑、反串等隐性表达的真实含义。\n\n"
            "**输出格式：**\n"
            "对每一方(官方、每个自媒体、评论区整体)给出：\n"
            "- 可信度评估(高/中/低 + 理由)\n"
            "- 利益相关度分析\n"
            "- 逻辑漏洞清单\n"
            "- 与其他来源的信息交叉验证结果"
        ),
        "en": (
            "The Scout has gathered raw intelligence on the event. Now unleash your inner skeptic "
            "and conduct ruthless cross-examination of every piece of information:\n\n"
            "**Review Dimensions:**\n"
            "1. **Cross-verification**: Compare descriptions of the same fact across sources — mark as consistent/inconsistent/unverifiable.\n"
            "2. **Interest Network Mapping**: Analyze the economic, political, or traffic motivations behind each voice. Who benefits? Who loses?\n"
            "3. **Logical Fallacy Diagnosis**: Check each argument for reasoning flaws (strawman, false dilemma, slippery slope, appeal to emotion, hasty generalization, etc.).\n"
            "4. **Bot/PR Detection**: Are there clusters of similar rhetoric in a short time window? Abnormal emotional polarization inconsistent with normal discussion?\n"
            "5. **Subtext & Sarcasm Decoding**: Identify passive-aggression, veiled mockery, and disguised stances.\n\n"
            "**Output Format:**\n"
            "For each party (official, each KOL, overall comment section):\n"
            "- Credibility assessment (High/Medium/Low + reasoning)\n"
            "- Interest analysis\n"
            "- Logical fallacy list\n"
            "- Cross-verification results against other sources"
        ),
    },
    "task.crew.challenger.expected": {
        "zh": (
            "一份详细的交叉审查报告，包含各方可信度评估、利益相关度分析、"
            "逻辑漏洞清单、以及信息交叉验证矩阵。"
        ),
        "en": (
            "A detailed cross-examination report containing credibility assessments, "
            "interest analyses, logical fallacy lists, and an information cross-verification matrix."
        ),
    },

    "task.crew.judge": {
        "zh": (
            "审核员已经对情报进行了交叉审查。现在请你以法官的身份，"
            "基于贝叶斯推断框架，对事件核心争议点进行裁决：\n\n"
            "**评分维度：**\n"
            "1. **明确核心争议主张**：首先用一句话写出要评估的具体命题(如'XX品牌汽车存在设计缺陷导致车门无法打开')\n"
            "2. **证据链完整性评分** (0-100)：\n"
            "   - 该核心主张有几条独立的直接证据？\n"
            "   - 证据之间的因果链是否闭合？有无缺失环节？\n"
            "   - 证据来源的多样性如何？(单一来源 vs 多方印证)\n"
            "3. **贝叶斯真相概率计算**：\n"
            "   - 给出先验概率P(H)：基于常识和统计，类似事件中该主张为真的基础概率\n"
            "   - 给出似然比LR：每条证据对主张的支持/削弱程度\n"
            "   - 计算出后验概率P(H|E)：综合所有证据后，核心主张为真的概率\n"
            "4. **缺失证据清单**：\n"
            "   - 列出要确证或证伪该主张还需要的关键证据\n"
            "   - 说明这些证据应该从何处获取\n\n"
            "**重要：**\n"
            "- 必须在报告开头明确写出你正在评估的核心争议主张\n"
            "- 必须给出具体的百分比数字，不能含糊其辞\n"
            "- 必须说明计算逻辑，不能只给结论\n"
            "- 对无法验证的主张明确标注'待证实'"
        ),
        "en": (
            "The Challenger has completed cross-examination. Now, as Judge, "
            "adjudicate the core controversy using Bayesian inference:\n\n"
            "**Scoring Dimensions:**\n"
            "1. **Identify the Core Claim**: First, state the specific proposition being evaluated in one sentence (e.g. 'Brand X vehicle has a design defect causing door failure')\n"
            "2. **Evidence Chain Completeness** (0-100):\n"
            "   - How many independent direct pieces of evidence support the core claim?\n"
            "   - Is the causal chain closed? Any missing links?\n"
            "   - How diverse are the evidence sources? (single source vs. multi-source corroboration)\n"
            "3. **Bayesian Truth Probability**:\n"
            "   - State prior probability P(H): base rate of similar claims being true, based on common sense and statistics\n"
            "   - State likelihood ratios LR: how strongly each piece of evidence supports/weakens the claim\n"
            "   - Compute posterior probability P(H|E): probability the core claim is true given all evidence\n"
            "4. **Missing Evidence List**:\n"
            "   - List key evidence still needed to confirm or refute the claim\n"
            "   - Specify where to obtain each piece\n\n"
            "**Important:**\n"
            "- Must explicitly state the core claim being evaluated at the top of the report\n"
            "- Must give specific percentage numbers — no ambiguity\n"
            "- Must explain the calculation logic — no conclusions without reasoning\n"
            "- Clearly mark unverifiable claims as 'Unverified'"
        ),
    },
    "task.crew.judge.expected": {
        "zh": (
            "一份包含以下内容的裁决报告：\n"
            "1. **核心争议主张**（明确写出要评估的命题，如'XX品牌汽车存在设计缺陷'）\n"
            "2. 该主张的证据链完整度评分(具体数字+理由)\n"
            "3. 贝叶斯推理过程(先验概率→似然比→后验概率)\n"
            "4. **综合真相可能概率**：该核心主张为真的后验概率(一个具体的百分比数字)\n"
            "5. 缺失的关键证据清单(至少3项)"
        ),
        "en": (
            "A judgment report containing:\n"
            "1. **Core Claim** (the specific proposition evaluated, e.g. 'Brand X vehicle has a design defect')\n"
            "2. Evidence chain completeness score for the claim (specific number + reasoning)\n"
            "3. Bayesian reasoning process (prior probability → likelihood ratios → posterior probability)\n"
            "4. **Overall Truth Probability**: posterior probability the core claim is true (a specific percentage)\n"
            "5. Missing key evidence list (at least 3 items)"
        ),
    },

    "task.crew.editor": {
        "zh": (
            "情报官、审核员、法官已经完成了全部分析。现在轮到你——首席撰稿人——"
            "将所有分析整合为一份可供公众阅读的结构化透视报告。\n\n"
            "**你必须严格按以下格式输出(使用纯Markdown)：**\n\n"
            "```markdown\n"
            "# 🔍 AI资讯透视报告\n\n"
            "## 📌 事件概述\n"
            "[5W1H纯事实总结，每条事实标注来源。不使用任何主观修饰词]\n\n"
            "## 📊 真相透视表\n"
            "> 本表评估的核心主张是：「[从法官报告中提取核心争议主张]」。以下概率值表示该主张为真的可能性。\n\n"
            "| 指标 | 数值 |\n"
            "|------|------|\n"
            "| 真相可能概率 | XX% |\n"
            "| 证据链完整度 | XX/100 |\n"
            "| 信息交叉验证率 | XX% |\n\n"
            "**概率计算依据**：[法官的贝叶斯推理简述]\n"
            "**缺失的关键证据**：\n"
            "1. [证据1 — 说明从何处获取]\n"
            "2. [证据2]\n"
            "3. [证据3]\n\n"
            "## ⚖️ 各方观点对垒\n"
            "### 🏛️ 官方/权威方\n"
            "[核心说辞 + 支撑证据 + 置信度评分]\n\n"
            "### 📢 自媒体/KOL方\n"
            "[逐一列出：核心说辞 + 利益相关度分析 + 逻辑漏洞]\n\n"
            "### 💬 评论区舆情\n"
            "**情绪占比**：[angry/fearful/neutral/supportive/sarcastic等，给出百分比]\n"
            "**代表性神评**：[选取2-3条，分析其洞察价值]\n"
            "**反转信号**：[是否存在舆论反转的迹象]\n\n"
            "## 🔍 事实链条对齐\n"
            "### ✅ 已确认事实\n"
            "[多方交叉验证通过的事实，逐条标注来源]\n"
            "### ⚠️ 存疑点\n"
            "[证据不足或来源单一的说法]\n"
            "### ❌ 矛盾点\n"
            "[各方说法存在直接冲突的地方，列出冲突双方及其说辞]\n"
            "```\n\n"
            "**关键约束：**\n"
            "1. 任何数字、事实、百分比必须来自上游Agent的输出，严禁自行编造\n"
            "2. 每条事实性陈述必须带来源标记 [来源: xxx]\n"
            "3. 明确区分'事实'和'观点/推断'\n"
            "4. 不确定的地方标注'待证实'，不要强行得出结论"
        ),
        "en": (
            "The Scout, Challenger, and Judge have completed their analysis. Now it's your turn — "
            "Chief Editor — to integrate everything into a structured report for public reading.\n\n"
            "**You must strictly follow this output format (plain Markdown):**\n\n"
            "```markdown\n"
            "# 🔍 AI Vision Lens Report\n\n"
            "## 📌 Event Overview\n"
            "[5W1H factual summary. Cite sources for each fact. No subjective modifiers]\n\n"
            "## 📊 Truth Dashboard\n"
            "> The core claim under review: 「[Extract from Judge's report]」. The probability below represents the likelihood this claim is true.\n\n"
            "| Metric | Value |\n"
            "|------|------|\n"
            "| Truth Probability | XX% |\n"
            "| Evidence Completeness | XX/100 |\n"
            "| Cross-verification Rate | XX% |\n\n"
            "**Probability Rationale**: [Summarize Judge's Bayesian reasoning]\n"
            "**Missing Key Evidence**:\n"
            "1. [Evidence item 1 — where to obtain]\n"
            "2. [Evidence item 2]\n"
            "3. [Evidence item 3]\n\n"
            "## ⚖️ Viewpoint Showdown\n"
            "### 🏛️ Official/Authority Side\n"
            "[Core narrative + supporting evidence + confidence score]\n\n"
            "### 📢 Independent Media/KOL Side\n"
            "[List individually: core narrative + interest analysis + logical fallacies]\n\n"
            "### 💬 Public Sentiment\n"
            "**Sentiment Breakdown**: [angry/fearful/neutral/supportive/sarcastic — give percentages]\n"
            "**Notable Comments**: [Pick 2-3 high-quality comments, note their insight value]\n"
            "**Reversal Signals**: [Any signs of opinion reversal]\n\n"
            "## 🔍 Fact Alignment\n"
            "### ✅ Confirmed Facts\n"
            "[Facts verified by multiple sources, cite sources for each]\n"
            "### ⚠️ Uncertain Points\n"
            "[Claims with insufficient evidence or single source]\n"
            "### ❌ Contradictions\n"
            "[Direct conflicts between sources — list conflicting parties and their claims]\n"
            "```\n\n"
            "**Key Constraints:**\n"
            "1. All numbers, facts, percentages must come from upstream agents — never fabricate\n"
            "2. Every factual statement must carry a source tag [Source: xxx]\n"
            "3. Clearly distinguish 'fact' from 'opinion/inference'\n"
            "4. Mark uncertainty honestly — say 'Unverified' when uncertain, don't force conclusions"
        ),
    },
    "task.crew.editor.expected": {
        "zh": (
            "一份完整的、格式规范的Markdown透视报告，包含事件概述、真相透视表、"
            "各方观点对垒、事实链条对齐四个核心板块。所有事实带来源标记。"
        ),
        "en": (
            "A complete, well-formatted Markdown analysis report containing four core sections: "
            "Event Overview, Truth Dashboard, Viewpoint Showdown, and Fact Alignment. "
            "All facts carry source tags."
        ),
    },

    # =========================================================================
    # ui/pages/instant.py — Inline LLM Prompts
    # =========================================================================

    "prompt.filter_relevant": {
        "zh": (
            "用户搜索的事件关键词：「{topic}」\n\n"
            "以下是搜索结果，请判断每条是否与用户搜索的事件直接相关：\n\n"
            "{items}\n\n"
            "只回复与事件相关的条目编号（用逗号分隔，如 1,3,5）。如果都不相关，回复 NONE。"
        ),
        "en": (
            "The user searched for: 「{topic}」\n\n"
            "Below are search results. Determine which items are directly related to the user's search:\n\n"
            "{items}\n\n"
            "Reply only with the numbers of relevant items (comma-separated, e.g. 1,3,5). If none are relevant, reply NONE."
        ),
    },

    "prompt.summarize_info": {
        "zh": (
            "请对以下关于「{topic}」的信息进行客观梳理，生成一份新闻稿式的资讯概述。\n\n"
            "要求：\n"
            "1. 用中文，像写新闻稿一样自然叙述，不要用「开端」「发展」「争议」等死板的小标题\n"
            "2. 5-8 段，内容覆盖：事件起因、经过、争议焦点、当前结果、后续影响（自然融入叙述中）\n"
            "3. 每个自然段末尾用上标索引标注信息来源，如 [1]、[2]\n"
            "4. 不要添加主观评价，纯资讯梳理\n"
            "5. 文末附「信息来源索引」列出每个编号对应的来源名称\n\n"
            "信息来源：\n"
            "{sources_text}"
        ),
        "en": (
            "Please provide an objective summary of the following information about「{topic}」in a news-report style.\n\n"
            "Requirements:\n"
            "1. Write in English, narrate naturally like a news article — no rigid sub-headers like 'Beginning' or 'Development'\n"
            "2. 5-8 paragraphs covering: cause, progression, controversy, current outcome, aftermath (woven naturally into the narrative)\n"
            "3. End each paragraph with superscript source citations like [1], [2]\n"
            "4. No subjective commentary — pure factual summary\n"
            "5. End with a 'Source Index' listing each numbered source\n\n"
            "Sources:\n"
            "{sources_text}"
        ),
    },

    "prompt.insight.analyze_opinion": {
        "zh": (
            "你是一位资深社交媒体舆论分析师。用户正在研究「{topic}」的社交网络争议。\n\n"
            "以下是搜集到的社交媒体讨论（含平台和日期标注）：\n\n"
            "{items_text}\n\n"
            "请深入分析并输出 JSON 格式结果（只输出 JSON，放在 ```json 代码块中）：\n\n"
            "{{\n"
            '  "topic_intro": "用2-3句话介绍这个话题/人物/事件的基本背景（中文）",\n'
            '  "is_meme": true/false,\n'
            '  "meme_info": {{"origin": "梗的起源（如适用）", "evolution": "传播和演变路径", "first_appeared": "最早出现时间/平台"}},\n'
            '  "camps": [\n'
            "    {{\n"
            '      "name": "阵营简称",\n'
            '      "size_estimate": 0,\n'
            '      "audience_profile": "什么样的人群持此观点",\n'
            '      "core_beliefs": "核心立场",\n'
            '      "key_arguments": ["论点"],\n'
            '      "emotional_tone": "愤怒/理性/嘲讽/同情/调侃/中立",\n'
            '      "typical_platforms": ["平台"],\n'
            '      "representative_quote": "代表性言论"\n'
            "    }}\n"
            "  ],\n"
            '  "communities": [\n'
            '    {{"name": "圈层名", "perspective": "该圈层的独特视角", "aligned_camp": "倾向阵营"}}\n'
            "  ],\n"
            '  "controversy_genes": [\n'
            '    {{"tag": "标签", "explanation": "解释"}}\n'
            "  ],\n"
            '  "timeline": [\n'
            '    {{"date": "YYYY-MM-DD或约YYYY-MM", "event": "关键事件", "significance": "引爆点/反转/平息/升级", "heat": 0}}\n'
            "  ],\n"
            '  "opinion_shifts": [\n'
            '    {{"from": "起初观点", "to": "后来转变", "trigger": "触发事件", "approx_date": "约YYYY-MM"}}\n'
            "  ],\n"
            '  "cross_platform_sentiment": {{}},\n'
            '  "sentiment_distribution": {{}},\n'
            '  "controversy_type": "争议类型",\n'
            '  "underlying_tension": "深层矛盾洞察"\n'
            "}}\n\n"
            "要求：\n"
            "- camps 识别 2-4 个主要阵营，各阵营 size_estimate 总和为 100%，基于搜索结果推断\n"
            "- communities 识别至少 1-2 个相关圈层\n"
            "- controversy_genes 提取至少 1-2 个争议基因标签\n"
            "- timeline 至少 3-5 个关键节点（如能识别），heat 为 0-100 的相对热度\n"
            "- cross_platform_sentiment: 只填实际出现在搜索结果中的平台，情绪值为 0-100 整数，总和不必为 100\n"
            "- sentiment_distribution: 整体情绪分布，值为 0-100 整数，总和不必为 100\n"
            "- ⚠️ 重要：所有数值必须是基于搜索结果的推断，无法判断的字段用空数组 [] 或空对象 {{}} 标记，不要编造数据\n"
            "- 如果搜索数据显示不足，用空对象/数组标记\n"
            "- 所有中文内容使用中文"
        ),
        "en": (
            "You are a senior social media opinion analyst. The user is researching the social media controversy around「{topic}」.\n\n"
            "Below are collected social media discussions (with platform and date annotations):\n\n"
            "{items_text}\n\n"
            "Analyze deeply and output JSON (output ONLY JSON in a ```json code block):\n\n"
            "{{\n"
            '  "topic_intro": "A 2-3 sentence introduction to this topic/person/event (in English)",\n'
            '  "is_meme": true/false,\n'
            '  "meme_info": {{"origin": "Origin of the meme (if applicable)", "evolution": "Spread and evolution path", "first_appeared": "Earliest appearance time/platform"}},\n'
            '  "camps": [\n'
            "    {{\n"
            '      "name": "Camp name",\n'
            '      "size_estimate": 0,\n'
            '      "audience_profile": "What kind of people hold this view",\n'
            '      "core_beliefs": "Core stance",\n'
            '      "key_arguments": ["Argument"],\n'
            '      "emotional_tone": "Angry/Rational/Sarcastic/Sympathetic/Playful/Neutral",\n'
            '      "typical_platforms": ["Platform"],\n'
            '      "representative_quote": "Representative quote"\n'
            "    }}\n"
            "  ],\n"
            '  "communities": [\n'
            '    {{"name": "Community name", "perspective": "Unique perspective of this community", "aligned_camp": "Leaning camp"}}\n'
            "  ],\n"
            '  "controversy_genes": [\n'
            '    {{"tag": "Tag", "explanation": "Explanation"}}\n'
            "  ],\n"
            '  "timeline": [\n'
            '    {{"date": "YYYY-MM-DD or approx YYYY-MM", "event": "Key event", "significance": "Trigger/Reversal/De-escalation/Escalation", "heat": 0}}\n'
            "  ],\n"
            '  "opinion_shifts": [\n'
            '    {{"from": "Initial opinion", "to": "Shifted to", "trigger": "Trigger event", "approx_date": "Approx YYYY-MM"}}\n'
            "  ],\n"
            '  "cross_platform_sentiment": {{}},\n'
            '  "sentiment_distribution": {{}},\n'
            '  "controversy_type": "Type of controversy",\n'
            '  "underlying_tension": "Deep contradiction insight"\n'
            "}}\n\n"
            "Requirements:\n"
            "- Identify 2-4 main camps; size_estimate values should sum to 100%, inferred from search results\n"
            "- Identify at least 1-2 relevant communities\n"
            "- Extract at least 1-2 controversy gene tags\n"
            "- Timeline: at least 3-5 key nodes if identifiable; heat is relative 0-100\n"
            "- cross_platform_sentiment: only include platforms actually appearing in search results; sentiment values are 0-100 integers, don't need to sum to 100\n"
            "- sentiment_distribution: overall sentiment distribution; values are 0-100 integers, don't need to sum to 100\n"
            "- ⚠️ IMPORTANT: All values must be inferred from search results. Use empty arrays [] or empty objects {{}} for undetermined fields — do NOT fabricate data\n"
            "- If search data is insufficient, mark with empty objects/arrays\n"
            "- All content must be in English"
        ),
    },

    "prompt.insight.synthesize_report": {
        "zh": (
            "你是一位深谙互联网文化的社会观察家。请围绕「{topic}」撰写一份**争议洞察报告**。\n\n"
            "## 舆论分析数据\n"
            "{analysis_json}\n"
            "{meme_section}\n\n"
            "## 部分原始素材（增加现场感）\n"
            "{quotes_text}\n\n"
            "## 写作要求\n\n"
            "写一份自然流畅的长文（约2000-3000字）。**严禁使用固定模板**——不要用\"一、二、三\"编号，不要用\"背景-发展-高潮-结局\"的套路结构。\n\n"
            "报告应该像一篇优秀的深度社会观察文章，自然覆盖：\n\n"
            "1. **开场**：用吸引人的方式引入话题——这是什么事件/人物/梗，为什么在社交媒体上引发讨论。如果是梗，像\"梗百科\"一样追溯起源和演变。\n\n"
            "2. **舆论阵营画像**：介绍2-4个主要意见阵营。对每个阵营——\n"
            "   - 他们是谁（人群画像）\n"
            "   - 他们主张什么\n"
            "   - 他们为什么这样想\n"
            "   - 用引号引用一条代表性言论\n\n"
            "3. **圈层视角**：不同圈层/社群（电竞圈、二次元、职场人、饭圈等）如何看待这件事，他们各自关注什么。\n\n"
            "4. **争议演变时间线**：这场争议是如何发展的——引爆点 → 扩散 → 可能的反转或平息。如果舆论发生了迁移，描述变化过程。\n\n"
            "5. **跨平台对比**：微博/知乎/豆瓣/小红书/B站/Reddit 各自呈现什么特点——哪个平台情绪化、哪个理性分析、哪个站队表态。\n\n"
            "6. **争议基因**：这场争议本质上触动了什么——是代际冲突、阶层焦虑、性别对立、身份政治，还是圈层隔阂？给出有洞察力的分析。\n\n"
            "7. **深度观察**：超越表面，给出一些值得深思的观察。\n\n"
            "## 风格要求\n"
            "- 语言流畅自然，像一篇优质自媒体深度文章\n"
            "- 有力但不偏激，保持观察者的距离感\n"
            "- 引用代表性言论用引号标注，增加现场感\n"
            "- 可以有锐利的洞察，但不要情绪化站队\n"
            "- 避免学术腔和说教感"
        ),
        "en": (
            "You are a social observer deeply versed in internet culture. Write a **Controversy Insight Report** about「{topic}」.\n\n"
            "## Opinion Analysis Data\n"
            "{analysis_json}\n"
            "{meme_section}\n\n"
            "## Selected Raw Material (for color and authenticity)\n"
            "{quotes_text}\n\n"
            "## Writing Requirements\n\n"
            "Write a natural, flowing long-form article (~1500-2500 words). **NO rigid templates** — no numbered sections, no 'background-development-climax-resolution' structure.\n\n"
            "The report should read like an excellent in-depth social observation piece, naturally covering:\n\n"
            "1. **Opening**: Introduce the topic in an engaging way — what is this event/person/meme, and why is it sparking discussion on social media. If it's a meme, trace its origin and evolution like a 'meme encyclopedia'.\n\n"
            "2. **Opinion Camp Profiles**: Introduce 2-4 main opinion camps. For each camp —\n"
            "   - Who they are (audience profile)\n"
            "   - What they advocate\n"
            "   - Why they think this way\n"
            "   - Quote a representative statement\n\n"
            "3. **Community Perspectives**: How different communities/subcultures view this — what each focuses on.\n\n"
            "4. **Controversy Timeline**: How the controversy evolved — trigger → spread → possible reversal or resolution. Describe opinion shifts if any.\n\n"
            "5. **Cross-Platform Comparison**: How Weibo/Zhihu/Douban/Reddit/X each present different characteristics — which is emotional, which is analytical, which is taking sides.\n\n"
            "6. **Controversy Genes**: What does this controversy fundamentally touch — generational conflict, class anxiety, gender divide, identity politics, or subculture barriers? Provide insightful analysis.\n\n"
            "7. **Deep Observations**: Go beyond the surface. Offer thought-provoking observations.\n\n"
            "## Style Requirements\n"
            "- Natural, flowing language — like a quality long-form article\n"
            "- Strong but not extreme — maintain observer's distance\n"
            "- Use quotation marks for representative quotes — adds authenticity\n"
            "- Sharp insights are welcome, but don't take sides emotionally\n"
            "- Avoid academic tone and preaching"
        ),
    },

    "prompt.should_search": {
        "zh": (
            "你是一个判断助手。用户刚读了关于「{topic}」的报告，现在有一个追问。\n\n"
            "## 报告内容摘要\n"
            "{report}\n\n"
            "## 用户追问\n"
            "{question}\n\n"
            "请判断：仅凭报告现有内容是否足以回答这个追问？\n"
            "- 如果报告内容足够 → 回复 NO\n"
            "- 如果报告信息不足/缺失/需要最新数据/需要验证 → 回复 YES\n\n"
            "只回复 YES 或 NO。"
        ),
        "en": (
            "You are a decision assistant. The user just read a report about「{topic}」and has a follow-up question.\n\n"
            "## Report Summary\n"
            "{report}\n\n"
            "## User's Question\n"
            "{question}\n\n"
            "Determine: Is the report content alone sufficient to answer this question?\n"
            "- If the report is sufficient → reply NO\n"
            "- If the report lacks information / needs latest data / needs verification → reply YES\n\n"
            "Reply only YES or NO."
        ),
    },

    "prompt.generate_answer": {
        "zh": (
            "你是新闻分析助手。用户刚阅读了关于「{topic}」的透视报告，现在追问。\n\n"
            "## 报告内容\n"
            "{report}{search_note}\n\n"
            "## 用户追问\n"
            "{question}\n\n"
            "要求：\n"
            "- 简洁直接，用中文\n"
            "- 优先引用报告中已有信息\n"
            "- 如果补充搜索有相关信息，引用并标注\"🔍 实时搜索\"\n"
            "- 信息不足的地方诚实说明"
        ),
        "en": (
            "You are a news analysis assistant. The user just read a report about「{topic}」and has a follow-up question.\n\n"
            "## Report Content\n"
            "{report}{search_note}\n\n"
            "## User's Question\n"
            "{question}\n\n"
            "Requirements:\n"
            "- Be concise and direct, in English\n"
            "- Prioritize citing information already in the report\n"
            "- If supplementary search results are relevant, cite them and mark \"🔍 Live Search\"\n"
            "- Honestly acknowledge where information is insufficient"
        ),
    },

    "prompt.disambiguate": {
        "zh": (
            "用户搜索关键词：「{topic}」\n\n"
            "搜索结果：\n"
            "{titles}\n\n"
            "判断：以上搜索结果是否指向**完全相同的一个事件**？\n"
            "- 如果所有结果都在报道同一事件（不同媒体不同角度也算同一个事件）→ 回复 SPECIFIC\n"
            "- 只有当前几条结果明显是**不同的事件**时才回复 AMBIGUOUS\n\n"
            "只回复 SPECIFIC 或 AMBIGUOUS。"
        ),
        "en": (
            "User search keyword: 「{topic}」\n\n"
            "Search results:\n"
            "{titles}\n\n"
            "Determine: Do all the above results point to **the exact same event**?\n"
            "- If all results cover the same event (different media/angles still counts as same event) → reply SPECIFIC\n"
            "- Only reply AMBIGUOUS if results clearly point to **different events**\n\n"
            "Reply only SPECIFIC or AMBIGUOUS."
        ),
    },

    "prompt.candidates_label": {
        "zh": "🔍 关键词较模糊，以下是可能的事件候选，请选择一个：",
        "en": "🔍 Vague keyword — here are possible matches. Please select one:",
    },

    # =========================================================================
    # tools/search_tool.py
    # =========================================================================

    "tool.search.description": {
        "zh": (
            "搜索指定话题的全网信息，返回官方通报、自媒体观点、社交媒体评论等多源数据。"
            "输入为话题关键词或URL链接。输出为结构化的JSON格式情报数据。"
        ),
        "en": (
            "Search the web for comprehensive information on a given topic. Returns multi-source data "
            "including official announcements, independent media opinions, and social media comments. "
            "Input: topic keywords or URL. Output: structured JSON intelligence data."
        ),
    },
    "tool.search.error": {
        "zh": "搜索失败：未配置搜索引擎 API Key 或搜索服务不可用。请在设置中配置搜索提供商。",
        "en": "Search failed: No search engine API Key configured or search service unavailable. Please configure a search provider in Settings.",
    },

    # =========================================================================
    # utils/weekly_news.py
    # =========================================================================

    "prompt.weekly_news.classify": {
        "zh": (
            "请对以下新闻逐条处理，返回 JSON 数组。每个元素格式：\n"
            '{{"id": 序号, "title_cn": "中文标题(简洁)", "region": "china/global", "controversy": "high/medium/low", "reason": "一句话说明为什么是这个争议等级"}}\n\n'
            "判断标准：\n"
            "- region: 与中国直接相关(政治/经济/社会/科技)→china，否则→global\n"
            "- controversy: 存在明显对立的观点/利益冲突/舆论反转→high，有一定讨论度→medium，纯资讯→low\n\n"
            "新闻列表：\n"
            "{items_text}\n\n"
            "只返回 JSON 数组，不要其他内容。"
        ),
        "en": (
            "Process each news item below and return a JSON array. Each element format:\n"
            '{{"id": number, "title_cn": "English title (concise)", "region": "china/global", "controversy": "high/medium/low", "reason": "One sentence explaining the controversy level"}}\n\n'
            "Criteria:\n"
            "- region: Directly related to China (politics/economy/society/tech) → china, otherwise → global\n"
            "- controversy: Clear opposing viewpoints/conflicts of interest/opinion reversal → high, moderate discussion → medium, pure news → low\n\n"
            "News items:\n"
            "{items_text}\n\n"
            "Return only the JSON array, nothing else."
        ),
    },

    # =========================================================================
    # Additional UI strings discovered during wrapping
    # =========================================================================

    "输入模型 ID，如 claude-sonnet-4-6": {
        "en": "Enter model ID, e.g. claude-sonnet-4-6"
    },
    "输入 API Key": {
        "en": "Enter API Key"
    },
    "正在测试分析 LLM 连接...": {
        "en": "Testing Analysis LLM connection..."
    },
    "正在测试情报 LLM 连接...": {
        "en": "Testing Intel LLM connection..."
    },

    # Onboarding dialog content
    "### 🎉 欢迎！开始之前请先配置 AI 模型\n\n"
    "本工具使用 **4-Agent CrewAI 辩论引擎** 进行深度资讯分析，需要至少配置一个 LLM 才能工作。\n\n"
    "**快速开始：**\n"
    "1. 点击下方按钮打开设置\n"
    "2. 在 **🔍 情报 LLM** 标签页选择厂商，填入 API Key\n"
    "3. 点击 **💾 保存设置**\n"
    "4. 点 **🧪 测试连接** 验证可用性\n\n"
    "> 💡 **推荐**：DeepSeek 便宜且中文能力强；DuckDuckGo 搜索免费无需 Key。\n"
    "> 所有配置保存在本地 `data/settings.json`，不会上传。": {
        "en": (
            "### 🎉 Welcome! Configure your AI model first\n\n"
            "This tool uses a **4-Agent CrewAI Debate Engine** for deep analysis and needs at least one LLM configured to work.\n\n"
            "**Quick Start:**\n"
            "1. Click the button below to open Settings\n"
            "2. In the **🔍 Intel LLM** tab, select a provider and enter your API Key\n"
            "3. Click **💾 Save Settings**\n"
            "4. Click **🧪 Test Connection** to verify\n\n"
            "> 💡 **Recommended**: DeepSeek is affordable with strong multilingual support; DuckDuckGo search is free, no Key needed.\n"
            "> All configuration is saved locally in `data/settings.json` — nothing is uploaded."
        ),
    },

    # Info mode LLM summary fallback
    "### 信息概述": {"en": "### Summary"},
    "*来源: {source}*": {"en": "*Source: {source}*"},
    "> ⚠️ 模板化摘要。配置 LLM API Key 可启用 AI 智能梳理。": {
        "en": "> ⚠️ Template summary. Configure an LLM API Key to enable AI-powered smart summaries."
    },

    # Insight template fallback
    "> ⚠️ 模板化摘要。配置 LLM API Key 可启用 AI 智能深度分析。": {
        "en": "> ⚠️ Template summary. Configure an LLM API Key to enable AI-powered deep analysis."
    },

    # Follow-up response
    "追问处理失败：": {"en": "Q&A failed: "},

    # Platform labels
    "通用": {"en": "General"},

    # Search query labels
    " 网友评论 舆论": {"en": " comments debate"},

    # Missing entries added during wrapping
    "辩论": {"en": "Debate"},
    "新闻获取失败": {"en": "News fetch failed"},
    "请检查搜索配置或尝试切换 DuckDuckGo。": {
        "en": "Please check search configuration or try switching to DuckDuckGo."
    },
    "📋 历史透视报告": {"en": "📋 Analysis History"},
    "📊 数据透视": {"en": "📊 Data Dashboard"},
    "SearXNG 实例地址": {"en": "SearXNG Instance URL"},
    "⚠️ 未配置 LLM API Key。争议洞察需要 LLM 进行深度分析。将使用模板化输出。": {
        "en": "⚠️ LLM API Key not configured. Insight mode requires LLM for deep analysis. Using template output."
    },

    # More missing entries
    "⚠️ 模板化摘要。配置 LLM API Key 可启用 AI 智能深度分析。": {
        "en": "⚠️ Template summary. Configure an LLM API Key to enable AI-powered deep analysis."
    },
    "你的关键词指向多个可能的事件，请选择一个：": {
        "en": "Your keyword matches multiple possible events. Please select one:"
    },
    "### 📋 信息梳理结果": {"en": "### 📋 Info Summary"},
    "### ⚔️ 需要深度分析？": {"en": "### ⚔️ Need Deeper Analysis?"},
    "### ⚔️ 需要更深度的事实核查？": {"en": "### ⚔️ Need Deeper Fact-Checking?"},
    "### 📊 争议洞察仪表盘": {"en": "### 📊 Controversy Insight Dashboard"},
    "#### 🔄 观点迁移": {"en": "#### 🔄 Opinion Shifts"},
    "#### 🧠 深层矛盾洞察": {"en": "#### 🧠 Underlying Tensions"},
    "#### 🎯 圈层视角": {"en": "#### 🎯 Community Perspectives"},
    "#### 来源分布": {"en": "#### Source Distribution"},
    "争议洞察": {"en": "Controversy Insight"},
    "✅ 4-Agent 辩论完成（耗时 {elapsed:.0f} 秒）": {
        "en": "✅ 4-Agent Debate complete ({elapsed:.0f}s)"
    },

    # App title
    "AI资讯透视镜": {"en": "Vision Lens"},

    # Template insight report labels
    "template.camps_title": {
        "zh": "舆论阵营（共 {count} 个）",
        "en": "Opinion Camps ({count} total)",
    },
    "template.camp_item": {
        "zh": "### {i}. {name}（约 {size}%）",
        "en": "### {i}. {name} (~{size}%)",
    },
    "template.camp_profile": {
        "zh": "- **人群画像**: {val}",
        "en": "- **Audience Profile**: {val}",
    },
    "template.camp_belief": {
        "zh": "- **核心立场**: {val}",
        "en": "- **Core Stance**: {val}",
    },
    "template.camp_args": {
        "zh": "- **主要论据**: {val}",
        "en": "- **Key Arguments**: {val}",
    },
    "template.camp_tone": {
        "zh": "- **情绪基调**: {val}",
        "en": "- **Emotional Tone**: {val}",
    },
    "template.camp_quote": {
        "zh": "- **代表性言论**: 「{val}」",
        "en": '- **Representative Quote**: "{val}"',
    },
    "template.communities_title": {
        "zh": "涉及圈层",
        "en": "Communities Involved",
    },
    "template.community_item": {
        "zh": "- **{name}**: {perspective}（倾向: {camp}）",
        "en": "- **{name}**: {perspective} (leans: {camp})",
    },
    "template.timeline_title": {
        "zh": "关键时间线",
        "en": "Key Timeline",
    },
    "template.genes_title": {
        "zh": "争议基因",
        "en": "Controversy Genes",
    },
    "template.tension_title": {
        "zh": "深层矛盾",
        "en": "Underlying Tensions",
    },
    "🧬 争议洞察：": {"en": "🧬 Controversy Insight: "},
    "未知阵营": {"en": "Unknown Camp"},
}

# ============================================================
# Public API
# ============================================================


def t(key: str, **kwargs) -> str:
    """Translate a key to the current session language.

    Resolution order:
    1. Look up key in _TRANSLATIONS.
       If found, use the entry for the current language (zh/en).
       For 'zh': if the zh entry is missing, return the key itself.
    2. If key not found in _TRANSLATIONS at all: return the key as-is.

    Args:
        key: Translation key. Short UI strings use the Chinese text itself.
             Long prompts use dotted names like "agent.scout.goal".
        **kwargs: Format arguments inserted via str.format().

    Returns:
        Translated and formatted string.
    """
    lang = _get_lang()
    entry = _TRANSLATIONS.get(key)

    if entry:
        result = entry.get(lang)
        if result is not None:
            pass  # Use the translation
        elif lang == "zh":
            # For zh, if no explicit zh entry, the key IS the Chinese text
            result = key
        else:
            # For en, if no en entry, fall back to key
            result = key
    else:
        # Key not in translations at all
        result = key

    if kwargs:
        try:
            result = result.format(**kwargs)
        except (KeyError, ValueError):
            # If format fails (e.g. key contains literal braces), return as-is
            pass

    return result


def _get_lang() -> str:
    """Get the current language from session state. Defaults to 'zh'."""
    try:
        return st.session_state.get("lang", "zh")
    except Exception:
        return "zh"


def init_language():
    """Load language preference from settings.json into session state.
    Call once at startup in app.py main(). Sets st.session_state.lang.
    Default: 'zh'.
    """
    if "lang" not in st.session_state:
        try:
            import json
            from pathlib import Path
            settings_file = Path(__file__).parent.parent / "data" / "settings.json"
            if settings_file.exists():
                saved = json.loads(settings_file.read_text(encoding="utf-8"))
                st.session_state.lang = saved.get("language", "zh")
            # If no settings file yet, don't default — language selection dialog handles first run
        except Exception:
            pass  # Don't set default; language dialog handles first run
