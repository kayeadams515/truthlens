@echo off
REM Build Vision Lens desktop app for Windows
setlocal

cd /d "%~dp0\.."

echo === Installing dependencies ===
pip install -r requirements.txt

echo === Building with PyInstaller ===
pyinstaller truthlens.spec --noconfirm --clean

echo.
echo === Build complete ===
echo Standalone binary: dist\VisionLens.exe

if exist "dist\VisionLens.exe" (
    echo Build successful.
) else (
    echo Build may have failed — check output above.
)
