# AI资讯透视镜 (Vision Lens)

> 穿透信息迷雾，还原事实本相 — 多智能体辩论引擎驱动的智能资讯分析工具

## 简介

AI资讯透视镜是一个基于多智能体辩论的新闻分析工具。核心思路是用多个 AI Agent 互相交叉验证，模拟「搜集→质疑→裁决→撰稿」的新闻编辑流程，而非依赖单一 LLM 直接输出结论。

### 分析模式

| 模式 | 入口 | 适用场景 | 底层 |
|------|------|---------|------|
| 📋 资讯模式 | Feed 页搜索 / 新闻卡片 | 快速了解事件全貌 | 多源搜索 + LLM 摘要 |
| ⚔️ 争议剖析 | 资讯模式结果下方输入框 | 对某一事件有具体疑问，想了解争议格局或核查真相 | 3-4 Agent 辩论流水线 |
| 🧬 争议洞察 | Feed 页搜索 / 新闻卡片 | 社交媒体原生争议、梗、八卦、热门话题 | LLM 舆论分析 |

### 智能自适应分析

两种深度模式均不采用固定模板，而是由 AI 先判定分析角度再组织输出：

**争议剖析 — 意图识别：**
- **了解争议格局**（"大家到底在吵什么"）→ 3-Agent 流水线，输出各方立场对垒、说法对齐、舆论情绪分布，不生成真相概率
- **真相核查**（"XX 说的是真的吗"）→ 4-Agent 完整流水线（含 Judge），基于贝叶斯推断计算真相概率

**争议洞察 — 话题类型自适应：**
- **争议** → 阵营画像、争议基因、跨平台对比
- **梗/迷因** → 起源追溯、演变路径、变体赏析、为什么火、文化意义
- **事件** → 事件还原、各方反应、关键事实、后续影响
- **现象** → 现象描摹、原因剖析、影响群体、趋势判断

### 核心架构：CrewAI 辩论引擎

| Agent | 角色 | 职责 |
|-------|------|------|
| 🔍 情报官 (Scout) | 信息搜集 | 从多源搜索中英文互联网，汇总官方通报、自媒体、社交媒体等维度的信息 |
| 🧐 审核员 (Challenger) | 交叉审查 | 对比不同来源的证据，标记互相印证或矛盾之处，挖掘利益关联 |
| ⚖️ 法官 (Judge) | 可信度评估 | 仅在真相核查模式启用，基于贝叶斯推断评估证据链完整性，计算真相概率 |
| ✍️ 撰稿人 (Editor) | 报告生成 | 根据意图/话题类型选择合适的角度，生成结构化 Markdown 报告 |

> 法官（Judge）仅在用户明确问"XX 是真的吗"等真相核查类问题时才参与流水线，避免在不适合的话题上强行编造无意义的真相概率。

### 功能特性

- 🏠 **首页资讯流** — 18 个 RSS 源 + 多引擎网络搜索，按争议度排序，LLM 分类翻译
- 📄 **三种分析模式** — 资讯梳理 / 意图自适应争议剖析 / 话题类型自适应舆论洞察
- 🧠 **智能自适应** — 自动判定话题类型和用户意图，避免模板化输出
- 🔍 **多搜索引擎** — 支持 Tavily / DuckDuckGo / Brave / SerpAPI / SearXNG
- 🌐 **中英文平衡** — 中文搜索国内站点（知乎、微博、B站、豆瓣等），英文搜索国际媒体和社交平台
- 💬 **Reddit 独立搜索** — 通过 Reddit 公共 API 捕获海外社区舆论
- 🎨 **9 家 LLM 厂商** — DeepSeek / Claude / OpenAI / Gemini / Moonshot / 智谱 / 通义千问 / Mistral / xAI Grok
- 🌍 **中英文界面切换** — 一键切换 UI 语言，中英文均完整覆盖
- 🛡️ **内容过滤** — 自动拦截色情、赌博、SEO 推广等垃圾内容
- 💾 **配置持久化** — 所有设置保存在本地 `data/settings.json`
- 🧪 **连接测试** — 一键测试 LLM 和搜索引擎是否可用
- 🐳 **Docker 部署** — 一行命令即可部署

## 快速开始

### 前提条件

- Python 3.10+
- pip

### 安装

```bash
git clone https://github.com/KayeAdams515/TruthLens.git
cd TruthLens
pip install -r requirements.txt
```

### 运行

```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501`

### 首次使用

1. 启动后会自动弹出 **欢迎引导窗口**
2. 点击「打开设置」→ 选择厂商、填入 API Key
3. 也可以切换到免费的 DuckDuckGo 搜索（无需 Key）
4. 点击「保存设置」→ 持久化到本地
5. 点击「测试连接」验证配置

> **推荐组合**：DeepSeek（便宜、中文能力强）+ DuckDuckGo（免费搜索）

### Docker 部署

```bash
docker build -t truthlens .
docker run -p 8501:8501 truthlens
```

## 配置

所有配置通过应用内 **设置弹窗** 完成，无需手动编辑配置文件。

### 支持的大语言模型

| 厂商 | 默认模型 | API 类型 |
|------|----------|----------|
| DeepSeek | deepseek-chat / deepseek-reasoner | 原生支持 |
| Anthropic Claude | claude-sonnet-4-6 / claude-opus-4-7 / claude-haiku-4-5 | 原生支持 |
| OpenAI | gpt-4o / gpt-4o-mini / gpt-4.1 / o3 / o4-mini | 原生支持 |
| Google Gemini | gemini-2.5-flash / gemini-2.5-pro | OpenAI 兼容 |
| Moonshot (月之暗面) | moonshot-v1-8k / 32k / 128k | OpenAI 兼容 |
| 智谱 GLM | glm-4-plus / glm-4-flash / glm-4 | OpenAI 兼容 |
| 通义千问 | qwen-max / qwen-plus / qwen-turbo | OpenAI 兼容 |
| Mistral AI | mistral-large / medium / small | 原生支持 |
| xAI Grok | grok-3-beta / grok-2 | OpenAI 兼容 |

### 支持的搜索引擎

| 引擎 | 需要 API Key | 域名过滤 | 全文搜索 |
|------|-------------|---------|---------|
| Tavily | 是 | 支持 | 支持 |
| DuckDuckGo | 否 | 不支持 | — |
| Brave Search | 是（免费 2000次/月） | 支持 | — |
| SerpAPI | 是 | 支持 | — |
| SearXNG | 需自建实例 | 不支持 | — |

## 项目结构

```
TruthLens/
├── app.py                    # Streamlit 入口，会话管理，设置 UI
├── config.py                 # LLM 配置工厂，厂商元数据，搜索域名
├── requirements.txt          # Python 依赖
├── Dockerfile                # Docker 构建文件
│
├── agents/                   # CrewAI Agent 工厂
│   ├── scout.py              # 情报官 — 信息搜集
│   ├── challenger.py         # 审核员 — 交叉审查
│   ├── judge.py              # 法官 — 可信度评分（仅真相核查模式）
│   ├── editor.py             # 撰稿人 — 自适应角度报告生成
│   └── crew.py               # Crew 编排，条件构建 3/4 Agent 流水线
│
├── tools/                    # CrewAI Tools
│   └── search_tool.py        # 实时搜索工具（多源 + Reddit）
│
├── utils/                    # 工具模块
│   ├── i18n.py               # 中英文翻译（含所有 LLM 提示词）
│   ├── search.py             # 双语搜索，域名分拆，内容过滤
│   ├── search_providers.py   # 多搜索引擎适配层 + Reddit API
│   ├── news_sources.py       # RSS 聚合（18 个源）
│   ├── weekly_news.py        # 每周热点抓取 + LLM 分类翻译
│   ├── persistence.py        # 报告持久化
│   └── logger.py             # 日志
│
└── ui/                       # Streamlit 界面
    ├── styles.py             # 主题样式
    ├── components.py         # 通用组件（仪表盘、图表）
    └── pages/
        ├── feed.py           # 首页 — 热点资讯流 + 搜索入口
        └── instant.py        # 详情 — 三种分析模式 + 仪表盘
```

## 数据隐私

- 所有 API Key 和配置保存在本地 `data/settings.json`，不会上传
- 搜索查询和 LLM 请求直接发送到对应 API 端点
- 无遥测，无第三方追踪
