# AI资讯透视镜 (Vision Lens)

> 穿透信息迷雾，还原事实本相 — 4-Agent CrewAI 辩论引擎驱动的智能资讯分析工具

## 简介

AI资讯透视镜是一个基于多智能体辩论的新闻分析工具。它针对用户输入的话题，自动搜索中英文互联网、搜集多源信息，通过 **4 个 AI Agent 角色辩论** 的方式，交叉验证事实、挖掘利益关联、评估可信度，最终生成结构化的深度分析报告。

### 核心架构：4-Agent 辩论引擎

| Agent | 角色 | 职责 |
|-------|------|------|
| 🔍 情报官 (Scout) | 信息搜集 | 从多源搜索中英文互联网，汇总官方通报、自媒体、社交媒体等维度的信息 |
| 🧐 杠精审核员 (Challenger) | 交叉审查 | 对比不同来源的证据，标记互相印证或矛盾之处，挖掘利益关联 |
| ⚖️ 理性法官 (Judge) | 可信度评估 | 基于贝叶斯推断框架，对每个核心主张评估证据链完整性(0-100%) |
| ✍️ 首席撰稿人 (Editor) | 报告生成 | 整合分析成果，生成结构化 Markdown 报告，附带引用来源链接 |

### 功能特性

- 🏠 **首页资讯流** — 自动拉取本周中英文热点新闻，按争议度排序，翻译为中文标题
- 📄 **话题深度分析** — 输入任意话题，触发 4-Agent 辩论流程，生成完整透视报告
- 🔍 **多搜索引擎** — 支持 Tavily / DuckDuckGo / Brave / SerpAPI / SearXNG，可自由切换
- 🌐 **中英文平衡** — 中文搜索国内站点（知乎、微博、澎湃等），英文搜索国际媒体（BBC、Reuters 等）
- 🧠 **9 家 LLM 厂商** — DeepSeek / Claude / OpenAI / Gemini / Moonshot / 智谱 / 通义千问 / Mistral / xAI Grok
- 💾 **配置持久化** — 所有设置（API Key、模型选择、搜索域名）保存在本地，下次启动自动加载
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

所有配置通过应用内 **设置弹窗** 完成，保存在 `data/settings.json`，无需手动编辑配置文件。

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

| 引擎 | 需要 API Key | 域名过滤 |
|------|-------------|---------|
| DuckDuckGo | 否 | 不支持 |
| Tavily | 是 | 支持 |
| Brave Search | 是（免费 2000次/月） | 支持 |
| SerpAPI | 是 | 支持 |
| SearXNG | 需自建实例 | 不支持 |

## 项目结构

```
TruthLens/
├── app.py                    # Streamlit 入口，会话管理，设置 UI
├── config.py                 # LLM 配置工厂，厂商元数据
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
│   ├── search_tool.py        # 实时搜索工具
│   └── mock_data.py          # 模拟演示数据
│
├── utils/                    # 工具模块
│   ├── search.py             # 双语搜索，域名分拆，内容过滤
│   ├── search_providers.py   # 多搜索引擎适配层
│   ├── weekly_news.py        # 每周热点抓取与缓存
│   └── logger.py             # 日志
│
└── ui/                       # Streamlit 界面
    ├── styles.py             # 主题样式
    ├── components.py         # 通用组件
    └── pages/
        ├── feed.py           # 首页 — 热点资讯流
        └── instant.py        # 详情 — 话题深度分析
```

## 技术栈

- **[Streamlit](https://streamlit.io)** — Web UI 框架
- **[CrewAI](https://crewai.com)** — 多智能体编排
- **[LiteLLM](https://litellm.ai)** — LLM 统一接口（通过 CrewAI 调用）
- **[Tavily](https://tavily.com) / DuckDuckGo / Brave / SerpAPI** — 搜索引擎

## 数据隐私

- 所有 API Key 和配置保存在本地 `data/settings.json`，不会上传
- 搜索查询和 LLM 请求直接发送到对应 API 端点
- 无遥测，无第三方追踪
