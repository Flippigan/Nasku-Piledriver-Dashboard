"""Windows launcher - starts Streamlit server and opens browser."""

import time
_start = time.time()
def _log(msg):
    print(f"[{time.time() - _start:7.2f}s] {msg}", flush=True)

_log("launcher.py started")

import os
import sys
import socket
import subprocess
import threading
import webbrowser
from pathlib import Path

_log("stdlib imports complete")


def find_free_port():
    """Find an available port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def wait_for_server(port: int, timeout: int = 30) -> bool:
    """Wait for the Streamlit server to be ready."""
    _log(f"wait_for_server: polling port {port} (timeout={timeout}s)")
    start = time.time()
    attempt = 0
    while time.time() - start < timeout:
        attempt += 1
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect(("localhost", port))
                _log(f"wait_for_server: connected on attempt {attempt}")
                return True
        except (ConnectionRefusedError, socket.timeout):
            if attempt % 10 == 0:  # Log every 10 attempts (~5 seconds)
                _log(f"wait_for_server: still waiting (attempt {attempt})")
            time.sleep(0.5)
    _log(f"wait_for_server: TIMEOUT after {attempt} attempts")
    return False


def get_base_path() -> Path:
    """Get the base path, handling PyInstaller bundle."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent.parent


def get_app_path() -> Path:
    """Get the path to app.py."""
    return get_base_path() / "src" / "app.py"


def main():
    _log("main() entered")

    # Load bundled .env for Supabase credentials
    _log("importing dotenv")
    from dotenv import load_dotenv
    _log("dotenv imported")

    env_path = get_base_path() / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        _log(f"loaded .env from {env_path}")

    port = find_free_port()
    app_path = get_app_path()
    url = f"http://localhost:{port}"

    # Set up environment
    env = os.environ.copy()
    env["STREAMLIT_SERVER_PORT"] = str(port)
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    # Start Streamlit
    if getattr(sys, "frozen", False):
        # In frozen app, use the bundled streamlit
        _log("about to import streamlit.web.cli (HEAVY - this may take a while)")
        import streamlit.web.cli as stcli
        _log("streamlit.web.cli imported successfully")

        # Run in a thread so we can open browser
        def run_streamlit():
            _log("streamlit thread: starting stcli.main()")
            sys.argv = ["streamlit", "run", str(app_path),
                       "--server.port", str(port),
                       "--server.headless", "true",
                       "--browser.gatherUsageStats", "false"]
            stcli.main()

        server_thread = threading.Thread(target=run_streamlit, daemon=True)
        server_thread.start()
        _log("streamlit server thread started")
    else:
        # Development mode - use subprocess
        subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(app_path),
             "--server.port", str(port),
             "--server.headless", "true"],
            env=env,
        )

    # Wait for server and open browser
    _log(f"waiting for server at {url}")
    print(f"Starting Inverter Tracker on {url}...")
    if wait_for_server(port):
        _log("server ready, opening browser")
        webbrowser.open(url)
        _log("browser opened")
        print("Application started. Close this window to stop the server.")
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
    else:
        _log("ERROR: server failed to start within timeout")
        print("Error: Server failed to start. Check your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
