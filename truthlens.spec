# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Vision Lens single-executable packaging."""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect hidden imports for key packages
hidden_imports = [
    # Streamlit
    "streamlit", "streamlit.web", "streamlit.runtime", "streamlit.elements",
    "streamlit.watcher", "streamlit.components",
    "tornado", "watchdog", "altair", "pandas", "numpy",
    # Plotly
    "plotly", "plotly.express", "plotly.graph_objects",
    # CrewAI
    "crewai", "crewai.agents", "crewai.tasks", "crewai.tools",
    "crewai.llm", "crewai.utilities",
    # LiteLLM (CrewAI's backend)
    "litellm", "litellm.llms",
    # LangChain
    "langchain", "langchain_core", "langchain_anthropic",
    # Transport
    "httpx", "aiohttp", "urllib3",
    # Utils
    "pydantic", "yaml", "dotenv", "loguru", "uuid",
    # jaraco (setuptools deps)
    "jaraco.text", "jaraco.context", "jaraco.functools",
]

# Collect all submodules
for pkg in ["streamlit", "crewai", "plotly", "litellm", "langchain_core"]:
    try:
        hidden_imports.extend(collect_submodules(pkg))
    except Exception:
        pass

# Collect data files (static assets, etc.)
datas = []
for pkg in ["streamlit"]:
    try:
        datas.extend(collect_data_files(pkg))
    except Exception:
        pass

# Include project files
project_files = [
    ("app.py", "."),
    ("config.py", "."),
    ("requirements.txt", "."),
    (".env.example", "."),
]
# Walk and include all Python modules
for root, dirs, files in os.walk("."):
    # Skip build artifacts
    dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", ".claude", "build", "dist", "logs")]
    for f in files:
        if f.endswith(".py") or f.endswith(".txt"):
            full = os.path.join(root, f)
            dest = os.path.dirname(full)
            project_files.append((full, dest))

a = Analysis(
    ["run_app.py"],
    pathex=[],
    binaries=[],
    datas=datas + project_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "test", "unittest", "pytest", "setuptools"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="VisionLens",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No terminal window on macOS/Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Single executable only (no .app bundle — user runs from terminal or creates alias)
