#!/usr/bin/env python3
"""
Neon Racing — one-click launcher.

All you need installed is Python. This script does everything else:
  1. Installs any missing backend dependencies (Flask, SocketIO, etc.)
  2. Creates the local database the first time it's run
  3. Starts the game server (single-player + multiplayer both live here)
  4. Opens the game in your browser automatically

Just double-click this file (or run `python play.py` / `python3 play.py`).
"""
import os
import subprocess
import sys
import threading
import time
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
PORT = int(os.environ.get("PORT", 5000))


def _pip_install():
    print("📦 Checking dependencies (first run may take a minute)...")
    req = os.path.join(BACKEND, "requirements.txt")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", req],
        check=True,
    )


def _deps_missing():
    try:
        import flask  # noqa: F401
        import flask_sqlalchemy  # noqa: F401
        import flask_socketio  # noqa: F401
        import flask_jwt_extended  # noqa: F401
        import flask_cors  # noqa: F401
        return False
    except ImportError:
        return True


def _init_db_if_needed():
    db_path = os.path.join(BACKEND, "instance", "dev.db")
    if os.path.exists(db_path):
        return
    print("🗄️  Setting up the local database...")
    subprocess.run(
        [sys.executable, os.path.join("scripts", "init_db.py")],
        check=True,
        cwd=BACKEND,
    )


def _open_browser_soon():
    def _open():
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{PORT}")
    threading.Thread(target=_open, daemon=True).start()


def main():
    if _deps_missing():
        _pip_install()
    else:
        print("📦 Dependencies already installed.")

    _init_db_if_needed()

    sys.path.insert(0, BACKEND)
    os.chdir(BACKEND)

    from app import create_app
    from app.extensions import socketio

    app = create_app()

    print()
    print("🏁 Neon Racing is starting...")
    print(f"   Open http://localhost:{PORT} if your browser doesn't pop up.")
    print("   Turn on 'Multiplayer' in the menu to race with anyone else")
    print("   connected to this same server.")
    print("   Press CTRL+C to stop the server.")
    print()

    _open_browser_soon()
    socketio.run(app, host="0.0.0.0", port=PORT, debug=False, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
