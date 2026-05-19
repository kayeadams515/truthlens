"""Launcher script — starts Streamlit server and opens browser.

This is the entry point for PyInstaller packaging.
"""

import os
import sys
import time
import threading
import webbrowser


def main():
    # Ensure we're in the right directory (PyInstaller unpacks to sys._MEIPASS)
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(base_dir)

    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8501")

    threading.Thread(target=open_browser, daemon=True).start()

    # Start Streamlit server
    from streamlit.web import cli as st_cli
    sys.argv = ["streamlit", "run", "app.py",
                "--server.port=8501",
                "--server.headless=true",
                "--server.enableCORS=false",
                "--browser.serverAddress=localhost",
                "--server.address=0.0.0.0",
                ]
    st_cli.main()


if __name__ == "__main__":
    main()
