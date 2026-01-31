"""Windows launcher - starts Streamlit server and opens browser."""

import os
import sys
import socket
import subprocess
import threading
import time
import webbrowser
from pathlib import Path


def find_free_port():
    """Find an available port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def wait_for_server(port: int, timeout: int = 30) -> bool:
    """Wait for the Streamlit server to be ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect(("localhost", port))
                return True
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.5)
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
    # Load bundled .env for Supabase credentials
    from dotenv import load_dotenv
    env_path = get_base_path() / ".env"
    if env_path.exists():
        load_dotenv(env_path)

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
        import streamlit.web.cli as stcli

        # Run in a thread so we can open browser
        def run_streamlit():
            sys.argv = ["streamlit", "run", str(app_path),
                       "--server.port", str(port),
                       "--server.headless", "true",
                       "--browser.gatherUsageStats", "false"]
            stcli.main()

        server_thread = threading.Thread(target=run_streamlit, daemon=True)
        server_thread.start()
    else:
        # Development mode - use subprocess
        subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(app_path),
             "--server.port", str(port),
             "--server.headless", "true"],
            env=env,
        )

    # Wait for server and open browser
    print(f"Starting Inverter Tracker on {url}...")
    if wait_for_server(port):
        webbrowser.open(url)
        print("Application started. Close this window to stop the server.")
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
    else:
        print("Error: Server failed to start. Check your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
