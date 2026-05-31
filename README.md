[**中文**](README.zh.md) | **English**

# TruthLens (AI资讯透视镜 / Vision Lens)

> Pierce through the information fog and uncover the truth — a multi-agent debate engine for intelligent news analysis.

TruthLens uses multiple AI agents to cross-verify information, simulating a full editorial pipeline of **Gather → Challenge → Judge → Write**, rather than relying on a single LLM's direct output.

## Features

### Three Analysis Modes

| Mode | Entry | Use Case | How It Works |
|------|-------|----------|-------------|
| 📋 **Quick Info** | Home search bar / news cards | Get a fast overview of an event or topic | Multi-source search + LLM summarization |
| ⚔️ **Controversy Analysis** | Enter an opinion below search results | Question a claim, compare opposing views, or verify facts | 3–4 Agent debate pipeline + Bayesian truth probability |
| 🧬 **Controversy Insight** | Home search bar (Insight tab) / news cards | Understand social media controversies, memes, gossip, or trending phenomena | LLM-driven deep opinion analysis with adaptive framing |

### Adaptive Intelligence (Controversy Analysis & Insight)

Both deep analysis modes adapt their output framework based on the AI's detection of your intent or topic type:

**Controversy Analysis — Intent Recognition:**
- *"What are people arguing about?"* → 3-Agent pipeline: Scout → Challenger → Editor. Outputs stance comparison and opinion distribution.
- *"Is this claim true?"* → Full 4-Agent pipeline (includes Judge). Bayesian inference computes a truth probability score.

**Controversy Insight — Topic Adaptation:**
| Detectable Topic Type | Output Structure |
|----------------------|-----------------|
| Controversy | Stance profiles, controversy DNA, cross-platform comparison |
| Meme | Origin tracing, evolution path, variant gallery, cultural significance |
| Event | Timeline reconstruction, stakeholder reactions, key facts, aftermath analysis |
| Phenomenon | Description, root cause analysis, affected groups, trend projection |

### CrewAI Debate Engine

| Agent | Role | Responsibilities |
|-------|------|-----------------|
| 🔍 **Scout** | Intelligence Gatherer | Multi-source search across Chinese & English internet, aggregating official reports, social media, and independent sources |
| 🧐 **Challenger** | Cross-Examiner | Cross-references evidence across sources, flags corroborations and contradictions, surfaces potential bias or conflicts of interest |
| ⚖️ **Judge** | Credibility Assessor | Truth-seeking mode only. Bayesian inference over the evidence chain, computing a calibrated truth probability |
| ✍️ **Editor** | Report Writer | Adapts angle and structure based on detected intent/topic type, produces structured Markdown reports |

## Quick Start

### Option 1: Desktop App (Recommended — no Python required)

Download the latest `AI资讯透视镜.app` release (macOS). Double-click to run. The first launch will open a setup wizard to configure your LLM API Key.

Build from source:
```bash
git clone https://github.com/KayeAdams515/TruthLens.git
cd TruthLens
pip install -r requirements.txt
./scripts/build.sh       # macOS → dist/AI资讯透视镜.app
```

### Option 2: Command Line

```bash
git clone https://github.com/KayeAdams515/TruthLens.git
cd TruthLens
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

### Option 3: Docker

```bash
docker build -t truthlens .
docker run -p 8501:8501 truthlens
```

### First-Time Setup

1. Launch the app → language selection and setup wizard will appear automatically
2. Click **Settings** → choose an LLM provider and enter your API Key
3. (Optional) Configure a search engine API key
4. Save and start using!

> **Recommended combo:** DeepSeek (affordable, strong in Chinese) + Tavily (generous free search credits)

## Supported LLM Providers

| Provider | Default Model | API Type |
|----------|---------------|----------|
| DeepSeek | deepseek-chat / deepseek-reasoner | Native |
| Anthropic Claude | claude-sonnet-4-6 / claude-opus-4-7 / claude-haiku-4-5 | Native |
| OpenAI | gpt-4o / gpt-4o-mini / gpt-4.1 / o3 / o4-mini | Native |
| Google Gemini | gemini-2.5-flash / gemini-2.5-pro | OpenAI-compatible |
| Moonshot (月之暗面) | moonshot-v1-8k / 32k / 128k | OpenAI-compatible |
| Zhipu GLM | glm-4-plus / glm-4-flash | OpenAI-compatible |
| Alibaba Qwen | qwen-max / qwen-plus / qwen-turbo | OpenAI-compatible |
| Mistral AI | mistral-large / medium / small | Native |
| xAI Grok | grok-3-beta / grok-2 | OpenAI-compatible |

Supports **dual LLM configuration**: you can assign different providers/models for search (Scout agent) and deep analysis (Challenger, Judge, Editor agents).

## Supported Search Engines

| Engine | API Key Required | Domain Filtering | Notes |
|--------|-----------------|-----------------|-------|
| [Tavily](https://tavily.com) | Yes | Supported | AI-optimized, full-text search |
| [Brave Search](https://brave.com/search) | Yes (2,000 free / month) | Supported | Independent index, privacy-friendly |
| [SerpAPI](https://serpapi.com) | Yes | Supported | Google results aggregation |
| [SearXNG](https://searxng.org) | Self-hosted instance | Not supported | Private meta-search engine |
| Reddit | No | — | Public API for community opinion |

## Updating

```bash
cd TruthLens
git pull
pip install -r requirements.txt
```

Rebuild the desktop app:
```bash
./scripts/build.sh
```

## Project Structure

```
TruthLens/
├── desktop_app.py             # Desktop launcher (PyInstaller entry point)
├── app.py                     # Streamlit entry point, session management, settings UI
├── config.py                  # LLM config factory, provider metadata, search domains
├── truthlens.spec             # PyInstaller build config
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker build file
│
├── agents/                    # CrewAI Agent factory
│   ├── scout.py               # Scout — intelligence gathering
│   ├── challenger.py          # Challenger — cross-examination
│   ├── judge.py               # Judge — Bayesian credibility scoring
│   ├── editor.py              # Editor — adaptive report generation
│   └── crew.py                # Crew orchestrator, conditional 3/4-agent pipeline
│
├── tools/
│   └── search_tool.py         # CrewAI real-time search tool
│
├── utils/
│   ├── i18n.py                # Chinese/English UI + LLM prompt translation
│   ├── search.py              # Bilingual search, domain splitting, content filtering
│   ├── search_providers.py    # Multi-engine search adapter + Reddit API
│   ├── news_sources.py        # RSS aggregation (17 Chinese & English feeds)
│   ├── weekly_news.py         # Weekly trending topics + LLM classification/translation
│   ├── persistence.py         # Report local persistence
│   ├── paths.py               # PyInstaller path compatibility layer
│   └── logger.py              # Structured logging
│
├── ui/
│   ├── styles.py              # Custom CSS theme
│   ├── components.py          # Shared components (dashboard, probability chart)
│   └── pages/
│       ├── feed.py            # Home — trending feed + search entry
│       └── instant.py         # Detail — three analysis modes
│
├── data/                      # Runtime data (not git-tracked)
│   └── settings.json.example  # Configuration template
│
└── scripts/
    ├── build.sh               # macOS build script
    └── build.bat              # Windows build script
```

## Desktop App Packaging

Uses PyInstaller + pywebview to package the app as a native desktop window:

- **Architecture**: Parent process launches a pywebview native window; child process runs Streamlit headless server
- **Window close**: Automatically terminates the Streamlit subprocess
- **User data**: Stored at `~/.truthlens/` (independent of the app bundle)
- **First launch**: Setup wizard guides API key configuration

```bash
# macOS
./scripts/build.sh
# Output: dist/AI资讯透视镜.app + dist/VisionLens (~187 MB)

# Windows
scripts\build.bat
# Output: dist\VisionLens.exe
```

## Data Privacy

- All API keys and configuration are stored locally — never uploaded
- Search and LLM requests go directly to the respective API endpoints
- No telemetry, no third-party tracking

## License

MIT
