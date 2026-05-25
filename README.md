# AI资讯透视镜 (Vision Lens)

> 穿透信息迷雾，还原事实本相 — 多智能体辩论引擎驱动的智能资讯分析工具

## 简介

AI资讯透视镜用多个 AI Agent 互相交叉验证，模拟「搜集 → 质疑 → 裁决 → 撰稿」的新闻编辑流程，而非依赖单一 LLM 直接输出结论。

### 三种分析模式

| 模式 | 入口 | 适用场景 | 原理 |
|------|------|---------|------|
| 📋 资讯模式 | 首页搜索框 / 新闻卡片 | 快速了解事件全貌 | 多源搜索 + LLM 摘要 |
| ⚔️ 争议剖析 | 资讯结果下方输入观点 | 对事件有具体质疑，想看争议格局或核查真相 | 3-4 Agent 辩论流水线 + 贝叶斯真相概率 |
| 🧬 争议洞察 | 首页搜索框（洞察标签）/ 新闻卡片 | 社交媒体争议、梗、八卦、热门现象 | LLM 深度舆论分析 |

### 智能自适应（争议剖析 & 争议洞察）

两种深度模式不套固定模板，由 AI 先判定角度再组织输出：

**争议剖析 — 用户意图识别：**
- 「大家到底在吵什么」→ 3-Agent 流水线，输出各方立场对垒、舆论分布
- 「XX 说的是真的吗」→ 4-Agent 完整流水线（含 Judge），贝叶斯推断计算真相概率

**争议洞察 — 话题类型自适应：**
- 争议 → 阵营画像、争议基因、跨平台对比
- 梗/迷因 → 起源追溯、演变路径、变体赏析、文化意义
- 事件 → 事件还原、各方反应、关键事实、后续影响
- 现象 → 现象描摹、原因剖析、影响群体、趋势判断

### CrewAI 辩论引擎

| Agent | 角色 | 职责 |
|-------|------|------|
| 🔍 情报官 Scout | 信息搜集 | 多源搜索中英文互联网，汇总官方通报、自媒体、社交媒体等多维度信息 |
| 🧐 审核员 Challenger | 交叉审查 | 对比不同来源证据，标记互相印证或矛盾之处，挖掘利益关联 |
| ⚖️ 法官 Judge | 可信度评估 | 仅真相核查模式启用，贝叶斯推断评估证据链，计算真相概率 |
| ✍️ 撰稿人 Editor | 报告生成 | 根据意图/话题类型选择角度，生成结构化 Markdown 报告 |

## 快速开始

### 方式一：桌面应用（推荐，无需安装 Python）

下载 `AI资讯透视镜.app`（macOS），双击运行。首次启动将弹出引导向导，配置 LLM API Key 即可使用。

构建桌面应用：

```bash
git clone https://github.com/KayeAdams515/TruthLens.git
cd TruthLens
pip install -r requirements.txt
./scripts/build.sh       # macOS → dist/AI资讯透视镜.app
```

### 方式二：命令行运行

```bash
git clone https://github.com/KayeAdams515/TruthLens.git
cd TruthLens
pip install -r requirements.txt
streamlit run app.py
```

浏览器访问 `http://localhost:8501`

### 方式三：Docker

```bash
docker build -t truthlens .
docker run -p 8501:8501 truthlens
```

### 首次使用

1. 启动后自动弹出语言选择 → 引导窗口
2. 点击「打开设置」→ 选择 LLM 厂商、填入 API Key
3. 可选：切换到 DuckDuckGo 搜索（免费，无需 Key）
4. 保存设置 → 开始使用

> 推荐组合：DeepSeek（便宜、中文能力强）+ DuckDuckGo（免费搜索）

## 支持的 LLM

| 厂商 | 默认模型 | API 类型 |
|------|----------|----------|
| DeepSeek | deepseek-chat / deepseek-reasoner | 原生支持 |
| Anthropic Claude | claude-sonnet-4-6 / claude-opus-4-7 / claude-haiku-4-5 | 原生支持 |
| OpenAI | gpt-4o / gpt-4o-mini / gpt-4.1 / o3 / o4-mini | 原生支持 |
| Google Gemini | gemini-2.5-flash / gemini-2.5-pro | OpenAI 兼容 |
| Moonshot 月之暗面 | moonshot-v1-8k / 32k / 128k | OpenAI 兼容 |
| 智谱 GLM | glm-4-plus / glm-4-flash | OpenAI 兼容 |
| 通义千问 | qwen-max / qwen-plus / qwen-turbo | OpenAI 兼容 |
| Mistral AI | mistral-large / medium / small | 原生支持 |
| xAI Grok | grok-3-beta / grok-2 | OpenAI 兼容 |

支持双 LLM 配置：搜索用的情报 LLM 和深度分析用的分析 LLM 可以分别选择不同厂商和模型。

## 支持的搜索引擎

| 引擎 | 需要 API Key | 域名过滤 | 特点 |
|------|-------------|---------|------|
| Tavily | 是 | 支持 | AI 优化，全文搜索 |
| DuckDuckGo | 否 | 不支持 | 免费，无需注册 |
| Brave Search | 是（免费 2000次/月） | 支持 | 独立索引，隐私友好 |
| SerpAPI | 是 | 支持 | Google 结果聚合 |
| SearXNG | 需自建实例 | 不支持 | 自托管元搜索引擎 |
| Reddit | 否 | — | 公共 API，海外社区舆论 |

## 项目结构

```
TruthLens/
├── desktop_app.py             # 桌面应用启动器（PyInstaller 入口）
├── app.py                     # Streamlit 入口，会话管理，设置 UI
├── config.py                  # LLM 配置工厂，厂商元数据，搜索域名
├── truthlens.spec             # PyInstaller 构建配置
├── requirements.txt           # Python 依赖
├── Dockerfile                 # Docker 构建文件
│
├── agents/                    # CrewAI Agent 工厂
│   ├── scout.py               # 情报官 — 信息搜集
│   ├── challenger.py          # 审核员 — 交叉审查
│   ├── judge.py               # 法官 — 贝叶斯可信度评分
│   ├── editor.py              # 撰稿人 — 自适应角度报告生成
│   └── crew.py                # Crew 编排，条件构建 3/4 Agent 流水线
│
├── tools/
│   └── search_tool.py         # CrewAI 实时搜索工具
│
├── utils/
│   ├── i18n.py                # 中英文界面 + LLM 提示词翻译
│   ├── search.py              # 双语搜索，域名分拆，内容过滤
│   ├── search_providers.py    # 多搜索引擎适配层 + Reddit API
│   ├── news_sources.py        # RSS 聚合（17 个中英文源）
│   ├── weekly_news.py         # 每周热点抓取 + LLM 分类翻译
│   ├── persistence.py         # 报告本地持久化
│   ├── paths.py               # PyInstaller 路径兼容层
│   └── logger.py              # 结构化日志
│
├── ui/
│   ├── styles.py              # 自定义 CSS 主题
│   ├── components.py          # 通用组件（仪表盘、概率图）
│   └── pages/
│       ├── feed.py            # 首页 — 热点资讯流 + 搜索入口
│       └── instant.py         # 详情 — 三种分析模式
│
├── data/                      # 运行时数据（不被 git 追踪）
│   └── settings.json.example  # 配置模板
│
└── scripts/
    ├── build.sh               # macOS 构建脚本
    └── build.bat              # Windows 构建脚本
```

## 桌面应用打包

使用 PyInstaller + pywebview 将应用打包为原生桌面窗口：

- **架构**：父进程启动 pywebview 原生窗口，子进程运行 Streamlit headless 服务器
- **窗口关闭**：自动终止 Streamlit 子进程
- **用户数据**：打包后自动存储到 `~/.truthlens/`（不影响应用包本身）
- **首次启动**：引导向导帮助用户配置 API Key

```bash
# macOS
./scripts/build.sh
# 产物：dist/AI资讯透视镜.app + dist/VisionLens（187MB）

# Windows
scripts\build.bat
# 产物：dist\VisionLens.exe
```

## 数据隐私

- 所有 API Key 和配置保存在本地，不会上传
- 搜索和 LLM 请求直接发送到对应 API 端点
- 无遥测，无第三方追踪
