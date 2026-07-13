import os

from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # socketio.run (instead of app.run) so the multiplayer websocket works too —
    # still just one command, no extra server needed.
    # debug=True locally is fine; Render runs this via gunicorn instead (see render.yaml)
    socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)
