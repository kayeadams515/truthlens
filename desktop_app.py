"""Desktop launcher for Vision Lens (AI资讯透视镜).

Starts Streamlit in a subprocess and wraps it in a native desktop window.
Entry point for PyInstaller packaging.

Pattern: the same binary serves two roles depending on CLI args:
  VisionLens                    → GUI launcher (pywebview window)
  VisionLens --server <port>    → Streamlit server process
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def get_app_dir():
    """Get the application directory (works in PyInstaller and dev)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def run_server_mode():
    """Run Streamlit server. Called when argv[1] == '--server'."""
    port = int(sys.argv[2])
    os.chdir(str(get_app_dir()))

    from streamlit.web import cli as st_cli
    sys.argv = [
        "streamlit", "run", "app.py",
        f"--server.port={port}",
        "--server.headless=true",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--server.address=0.0.0.0",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]
    st_cli.main()


def _wait_for_server(port: int, timeout: int = 30) -> bool:
    """Poll until Streamlit server responds to health checks."""
    import urllib.request
    url = f"http://127.0.0.1:{port}/healthz"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = urllib.request.urlopen(url, timeout=1)
            if resp.status == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def _find_free_port(start: int = 8501) -> int:
    """Find a free TCP port starting from `start`."""
    import socket
    port = start
    while port < start + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
        port += 1
    return start


def main():
    # Server mode: spawned by ourselves to run Streamlit
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        run_server_mode()
        return

    # GUI launcher mode
    app_dir = str(get_app_dir())
    port = _find_free_port(8501)

    # Spawn ourselves as the Streamlit server
    args = [sys.executable]
    if not getattr(sys, "frozen", False):
        args.append(__file__)
    args.extend(["--server", str(port), app_dir])

    server_proc = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        if not _wait_for_server(port):
            print("Error: Streamlit server did not start within 30 seconds.", file=sys.stderr)
            server_proc.kill()
            sys.exit(1)

        import webview
        webview.create_window(
            title="AI资讯透视镜 Vision Lens",
            url=f"http://127.0.0.1:{port}",
            width=1280,
            height=800,
            min_size=(800, 600),
            resizable=True,
        )
        webview.start()
    finally:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()
            server_proc.wait()


if __name__ == "__main__":
    main()
