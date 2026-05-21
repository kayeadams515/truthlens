# AI资讯透视镜 (Vision Lens)

> 穿透信息迷雾，还原事实本相 — 4-Agent CrewAI 辩论引擎驱动的智能资讯分析工具

## 简介

AI资讯透视镜是一个基于多智能体辩论的新闻分析工具。支持三种分析模式，覆盖从快速资讯梳理到社交媒体舆论洞察的全场景需求。

### 三种分析模式

| 模式 | 适用场景 | 耗时 | 输出 |
|------|---------|------|------|
| 📋 资讯模式 | 快速了解事件全貌 | 5-10 秒 | 新闻稿式概述 + 来源索引 |
| ⚔️ 争议模式 | 有对立说法的硬新闻，需核查事实 | 30-90 秒 | 结构化报告 + 真相概率仪表盘 |
| 🧬 争议洞察 | 社交媒体原生争议、梗、八卦、热门话题 | 20-40 秒 | 自然叙述深度长文 + 舆论格局仪表盘 |

### 核心架构：4-Agent 辩论引擎（争议模式）

| Agent | 角色 | 职责 |
|-------|------|------|
| 🔍 情报官 (Scout) | 信息搜集 | 从多源搜索中英文互联网，汇总官方通报、自媒体、社交媒体等维度的信息 |
| 🧐 杠精审核员 (Challenger) | 交叉审查 | 对比不同来源的证据，标记互相印证或矛盾之处，挖掘利益关联 |
| ⚖️ 理性法官 (Judge) | 可信度评估 | 基于贝叶斯推断框架，对核心主张评估证据链完整性，计算真相概率 |
| ✍️ 首席撰稿人 (Editor) | 报告生成 | 整合分析成果，生成结构化 Markdown 报告，附带引用来源链接 |

### 争议洞察模式特色

不查证真相，而是**理解争议本身**。通过社交媒体重搜索（微博、知乎、B站、豆瓣、贴吧、小红书、Reddit、X 等），AI 分析：

- **舆论阵营画像** — 识别 2-4 个意见阵营，估算规模、情绪基调、核心论点
- **圈层分析** — 识别涉及的亚文化圈层，各圈层的独特视角
- **争议基因标签** — 底层冲突类型（代际冲突、阶层焦虑、性别议题等）
- **时间线梳理** — 争议从引爆到扩散到可能的反转或平息
- **观点迁移追踪** — 舆论在关键事件前后的立场变化
- **跨平台对比** — 各平台的情绪分布和论调差异
- **梗百科** — 自动识别梗/网络用语类话题，追溯起源和传播路径

> ⚠️ 仪表盘中的数值（阵营占比、情绪分布等）均为 AI 基于搜索结果的定性估算，非精确统计数据。

### 功能特性

- 🏠 **首页资讯流** — RSS 聚合（18 个源）+ 网络搜索，按争议度排序，翻译为中文标题
- 📄 **三种分析模式** — 资讯梳理 / 4-Agent 争议辩论 / 社交媒体舆论洞察
- 🔍 **多搜索引擎** — 支持 Tavily / DuckDuckGo / Brave / SerpAPI / SearXNG，可自由切换
- 🌐 **中英文平衡** — 中文搜索国内站点（知乎、微博、B站、豆瓣等），英文搜索国际媒体和社交平台
- 💬 **Reddit 搜索** — 独立的 Reddit 公共 API 搜索，捕获海外社区舆论
- 🧠 **9 家 LLM 厂商** — DeepSeek / Claude / OpenAI / Gemini / Moonshot / 智谱 / 通义千问 / Mistral / xAI Grok
- 🛡️ **内容过滤** — 自动拦截色情、赌博、SEO 推广、虚假评价等垃圾内容
- 💾 **配置持久化** — 所有设置保存在本地 `data/settings.json`，重启自动加载
- 🧪 **连接测试** — 一键测试 LLM 和搜索引擎是否可用
- 🐳 **Docker 部署** — 提供 Dockerfile，一行命令即可部署

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
| Anthropic Claude | claude-sonnet-4-6 / opus-4-7 / haiku-4-5 | 原生支持 |
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

### 可搜索的社交媒体平台

| 平台 | 方式 |
|------|------|
| Reddit | 独立 API 搜索（无需 Key） |
| 微博、知乎、B站、豆瓣、贴吧、小红书 | 通过搜索引擎域名过滤 |
| X(Twitter)、YouTube、Facebook、Instagram、TikTok | 通过搜索引擎域名过滤 |

## 项目结构

```
TruthLens/
├── app.py                    # Streamlit 入口，会话管理，设置 UI
├── config.py                 # LLM 配置工厂，厂商元数据，搜索域名
├── run_app.py                # 打包启动脚本
├── requirements.txt          # Python 依赖
├── Dockerfile                # Docker 构建文件
├── truthlens.spec            # PyInstaller 打包配置
│
├── agents/                   # CrewAI Agent 工厂
│   ├── scout.py              # 情报官 — 信息搜集
│   ├── challenger.py         # 审核员 — 交叉审查
│   ├── judge.py              # 法官 — 可信度评分
│   ├── editor.py             # 撰稿人 — 报告生成
│   └── crew.py               # Crew 编排
│
├── tools/                    # CrewAI Tools
│   └── search_tool.py        # 实时搜索工具（多源 + Reddit）
│
├── utils/                    # 工具模块
│   ├── search.py             # 双语搜索，域名分拆，内容过滤
│   ├── search_providers.py   # 多搜索引擎适配层 + Reddit API
│   ├── news_sources.py       # RSS 聚合（18 个源，stdlib 解析）
│   ├── weekly_news.py        # 每周热点抓取 + RSS 补充 + LLM 分类
│   ├── persistence.py        # 报告持久化
│   └── logger.py             # 日志
│
└── ui/                       # Streamlit 界面
    ├── styles.py             # 主题样式
    ├── components.py         # 通用组件（仪表盘、图表）
    └── pages/
        ├── feed.py           # 首页 — 热点资讯流 + 搜索入口
        └── instant.py        # 详情 — 三种分析模式
```

## 数据隐私

- 所有 API Key 和配置保存在本地 `data/settings.json`，不会上传
- 搜索查询和 LLM 请求直接发送到对应 API 端点
- 无遥测，无第三方追踪
