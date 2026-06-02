# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app (development)
streamlit run app.py                # Opens at http://localhost:8501

# Build desktop app
./scripts/build.sh                  # macOS → dist/AI资讯透视镜.app + dist/VisionLens
scripts/build.bat                   # Windows → dist/VisionLens.exe

# Build with PyInstaller directly
pyinstaller truthlens.spec --noconfirm --clean

# Docker
docker build -t truthlens .
docker run -p 8501:8501 truthlens

# Run a single CrewAI analysis from the CLI (standalone test)
python -m agents.crew "some news topic"
```

There are no automated tests in this repo.

## Architecture

TruthLens (AI资讯透视镜 / Vision Lens) is a **Streamlit web app** that uses **CrewAI** to orchestrate a multi-agent debate pipeline for news analysis. It ships as both a web app and a **PyInstaller-packaged desktop app** (pywebview wraps Streamlit in a native window).

### Three analysis modes

| Mode | Engine | Description |
|------|--------|-------------|
| **Info** (`info`) | Direct LLM call via `_summarize_info()` | Multi-source search + LLM summarization. No CrewAI. |
| **Controversy** (`controversy`) | CrewAI 3–4 agent pipeline (`agents/crew.py`) | Scout → Challenger → (Judge) → Editor. Adaptive: 3-agent for debate understanding, 4-agent for truth-seeking with Bayesian probability. |
| **Insight** (`insight`) | 2-step direct LLM calls (`_analyze_opinion_camps` + `_synthesize_insight_report`) | Social media opinion analysis. Topic-type adaptive (controversy/meme/event/phenomenon). No CrewAI — faster, more creative. |

### CrewAI debate pipeline (`agents/`)

```
Scout (search_llm, temp=0.1)         — searches CN+EN web via TruthLensSearchTool
  ↓ context
Challenger (integration_llm, temp=0.3) — cross-examines evidence, maps interests, finds fallacies
  ↓ context
Judge (integration_llm, temp=0.1)     — ONLY in truth-seeking mode. Bayesian scoring.
  ↓ context
Editor (integration_llm, temp=0.1)    — produces structured Markdown report
```

The pipeline is **sequential** (`Process.sequential`). Tasks pass context via CrewAI's `context=[task_scout, task_challenger, ...]`.

### Dual LLM configuration

The app supports two separate LLM configurations:
- **`search_llm`** — used by the Scout agent and lightweight tasks (intent classification, relevance filtering, disambiguation)
- **`integration_llm`** — used by Challenger, Judge, Editor, info summarization, insight analysis, and Q&A

Both are configured independently in Settings (provider, model, API key, base URL). The config factory is in `config.py` — `create_search_llm()` and `create_integration_llm()` read from Streamlit session state.

### Key data flow

1. User enters a topic on the **Feed page** (`ui/pages/feed.py`) → stored in `st.session_state.analyze_topic` + `analyze_mode`
2. Routed to **Instant page** (`ui/pages/instant.py`) → `render_instant()` reads session state and dispatches to the correct mode
3. Results are cached in session state (`current_report`, `current_summary`, `current_insight_report`) for redisplay on reruns (e.g., Q&A)
4. Reports are persisted to disk via `utils/persistence.py` → `data/reports/` (dev) or `~/.truthlens/reports/` (bundled)

### Search architecture

- **`utils/search_providers.py`** — unified adapter for Tavily, Brave, SerpAPI, SearXNG. Each provider is a `_search_*` function; the `search()` function routes to the active one.
- **`utils/search.py`** — `bilingual_search()` splits queries into CN and EN domain sets, runs two provider searches, interleaves results. Contains extensive spam/SEO content filtering (`_filter_results()` with regex patterns, domain blocklists, title stop words).
- **`tools/search_tool.py`** — `TruthLensSearchTool` wraps `bilingual_search` + Reddit search as a CrewAI `BaseTool` for the Scout agent.

### i18n system (`utils/i18n.py`)

Two key patterns:
- **UI strings**: Chinese text IS the translation key. `t("选择页面")` → looks up `"en"` value in `_TRANSLATIONS`, falls back to the key itself (Chinese).
- **LLM prompts**: Named keys like `"agent.scout.goal"` with both `"zh"` and `"en"` values.
- Language is stored in `st.session_state.lang` (`"zh"` or `"en"`), persisted in settings.json.

### Session state management (`app.py`)

`app.py` is the Streamlit entry point. On startup it:
1. Initializes language (`init_language()`)
2. Loads persisted settings from `data/settings.json` into session state for both LLM slots, search provider, domain filters
3. Shows onboarding dialog if no LLM is configured
4. Renders sidebar with nav + status indicators + settings button
5. Settings dialog (`_settings_dialog`) is a `@st.dialog` with 3 tabs (search domains, intel LLM, analysis LLM) plus connection testing

Provider switching in settings auto-caches API keys/URLs via `llm_config_cache` so switching back doesn't require re-entry.

### API Key Protection (server deployment)

When deploying as a website, API keys are protected by:
- **Environment variable override**: Set `SEARCH_LLM_API_KEY`, `INTEGRATION_LLM_API_KEY`, `TAVILY_API_KEY`, `BRAVE_API_KEY`, or `SERPAPI_API_KEY` in the environment. These take precedence over any UI-configured values and are **not saveable to or readable from `settings.json`**.
- **Masked UI display**: After configuration, API keys are shown as masked text (e.g., `sk-••••fGhK`) in the settings dialog. Users must explicitly click "Change" to replace a key — the existing key is never displayed in plaintext.
- **Env-configured keys are read-only**: When set via env vars, the settings UI shows "Configured via environment variable (server read-only)" and no input field is rendered.
- **No disk persistence for env keys**: `_save_settings()` skips keys that came from environment variables, preventing them from being written to `data/settings.json`.

See `.env.example` for the full list of supported environment variables.

### Desktop packaging (`desktop_app.py` + `truthlens.spec`)

The same binary serves two roles:
- **GUI mode**: spawns itself as a subprocess with `--server <port>`, waits for Streamlit to be healthy, then opens a pywebview window pointing to `http://127.0.0.1:<port>`.
- **Server mode** (`--server <port>`): runs `streamlit run app.py` headless.

`truthlens.spec` is the PyInstaller config — collects data files from `streamlit`, `crewai`, and `langchain_core`, plus all project `.py` files. User data is stored at `~/.truthlens/` (separate from the app bundle).

### UI structure (`ui/`)

- `ui/styles.py` — custom CSS theme
- `ui/components.py` — reusable Plotly charts: `truth_probability_gauge()`, `sentiment_bar_chart()`, `evidence_radar_chart()`
- `ui/pages/feed.py` — home page: search bar, weekly hot news, report history
- `ui/pages/instant.py` — analysis page: dispatches to info/controversy/insight, renders dashboards, handles Q&A and disambiguation
