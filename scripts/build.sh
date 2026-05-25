#!/bin/bash
# Build Vision Lens desktop app for macOS
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Building with PyInstaller ==="
pyinstaller truthlens.spec --noconfirm --clean

echo ""
echo "=== Build complete ==="
echo "App bundle: dist/AI资讯透视镜.app"
echo "Standalone binary: dist/VisionLens"

if [ -d "dist/AI资讯透视镜.app" ]; then
    APP_SIZE=$(du -sh "dist/AI资讯透视镜.app" 2>/dev/null | cut -f1)
    echo "App size: $APP_SIZE"
fi
