# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Vision Lens (AI资讯透视镜) desktop app packaging.

Build:
    pyinstaller truthlens.spec --noconfirm --clean
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# -- Hidden imports -----------------------------------------------------------

hidden_imports = [
    # Streamlit + its server stack
    "streamlit",
    "streamlit.web",
    "streamlit.web.cli",
    "streamlit.runtime",
    "streamlit.elements",
    "streamlit.watcher",
    "streamlit.components",
    "tornado",
    "watchdog",
    "altair",
    "pandas",
    "numpy",
    # Plotly
    "plotly",
    "plotly.express",
    "plotly.graph_objects",
    # CrewAI
    "crewai",
    "crewai.agents",
    "crewai.tasks",
    "crewai.tools",
    "crewai.llm",
    "crewai.utilities",
    # LiteLLM (CrewAI's LLM backend)
    "litellm",
    "litellm.llms",
    # LangChain
    "langchain",
    "langchain_core",
    "langchain_anthropic",
    # HTTP / transport
    "requests",
    "httpx",
    "aiohttp",
    "urllib3",
    # Tavily search (used by the app at runtime)
    "tavily",
    # Serialization & config
    "pydantic",
    "yaml",
    "dotenv",
    "loguru",
    # Desktop window
    "webview",
    "webview.platforms.cocoa",
    "webview.js",
    "bottle",
]

# Collect submodules for tricky packages
for pkg in ["streamlit", "crewai", "plotly", "litellm", "langchain_core"]:
    try:
        hidden_imports.extend(collect_submodules(pkg))
    except Exception:
        pass

# -- Data files ---------------------------------------------------------------

datas = []

# Frontend static assets + translations needed at runtime
for pkg in ["streamlit", "crewai"]:
    try:
        datas.extend(collect_data_files(pkg))
    except Exception:
        pass

# Include .dist-info / .egg-info metadata for importlib.metadata.version() calls.
# Collect from the site-packages where streamlit is installed.
import site as _site
import streamlit as _st
_sp_dir = os.path.dirname(os.path.dirname(_st.__file__))
for _entry in os.listdir(_sp_dir):
    if _entry.endswith((".dist-info", ".egg-info")):
        _full = os.path.join(_sp_dir, _entry)
        if os.path.isdir(_full):
            for _root, _dirs, _files in os.walk(_full):
                for _f in _files:
                    _src = os.path.join(_root, _f)
                    _rel = os.path.relpath(os.path.dirname(_src), _sp_dir)
                    datas.append((_src, _rel))

# Project Python files
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in (
        "__pycache__", ".git", ".claude", "build", "dist", "logs",
    )]
    for f in files:
        if f.endswith(".py"):
            full = os.path.join(root, f)
            dest = os.path.dirname(full)
            datas.append((full, dest))

# Settings template (no real keys)
if os.path.exists("data/settings.json.example"):
    datas.append(("data/settings.json.example", "data"))

# -- Analysis -----------------------------------------------------------------

a = Analysis(
    ["desktop_app.py"],
    pathex=[],
    binaries=[],
    datas=datas,
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS .app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="AI资讯透视镜.app",
        icon=None,
        bundle_identifier="com.truthlens.visionlens",
        version="1.0.0",
        info_plist={
            "NSHighResolutionCapable": True,
            "CFBundleName": "AI资讯透视镜",
            "CFBundleDisplayName": "AI资讯透视镜 Vision Lens",
            "CFBundleShortVersionString": "1.0.0",
        },
    )
