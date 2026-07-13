"""Real-time multiplayer: every connected player is dropped into one shared
room ('main') so racing together needs zero setup — no room codes, no
matchmaking screen. State lives in memory only (a dict keyed by socket id),
which is intentional: it resets when the server restarts and never touches
the database, so it can't corrupt or conflict with anti-cheat / save data.

This is a "ghost" model, not authoritative physics: each client still runs
its own local simulation (own traffic, own hits, own scoring). The server
just relays where everyone else is (lane position + distance travelled) so
each client can draw other players' cars nearby. Good enough to race
alongside friends; not meant to be cheat-proof for competitive stakes.
"""
from flask import request
from flask_socketio import emit, join_room, leave_room

ROOM = "main"

# sid -> {"id", "name", "color", "carType", "x", "dist", "speed"}
players = {}


def _clamp(value, lo, hi, default=0.0):
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    if v != v:  # NaN
        return default
    return max(lo, min(hi, v))


def register_socket_handlers(socketio):
    @socketio.on("connect")
    def handle_connect():
        # Nothing to do yet — the client sends 'join' once it has a name.
        pass

    @socketio.on("join")
    def handle_join(data):
        data = data or {}
        sid = request.sid
        name = str(data.get("name") or "Racer")[:18].strip() or "Racer"
        color = str(data.get("color") or "#00ffcc")[:9]
        car_type = str(data.get("carType") or "car")[:24]

        join_room(ROOM)
        players[sid] = {
            "id": sid,
            "name": name,
            "color": color,
            "carType": car_type,
            "x": 0.0,
            "dist": 0.0,
            "speed": 0.0,
        }

        # Send the newcomer everyone already racing, then tell everyone else
        # about the newcomer.
        emit("roster", [p for s, p in players.items() if s != sid])
        emit("player_joined", players[sid], to=ROOM, include_self=False)

    @socketio.on("state")
    def handle_state(data):
        data = data or {}
        sid = request.sid
        p = players.get(sid)
        if not p:
            return
        p["x"] = _clamp(data.get("x"), -20, 20, p["x"])
        p["dist"] = _clamp(data.get("dist"), 0, 10_000_000, p["dist"])
        p["speed"] = _clamp(data.get("speed"), 0, 2000, p["speed"])
        emit("player_state", p, to=ROOM, include_self=False)

    @socketio.on("leave")
    def handle_leave():
        sid = request.sid
        if sid in players:
            del players[sid]
        leave_room(ROOM)
        emit("player_left", {"id": sid}, to=ROOM)

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        if sid in players:
            del players[sid]
            emit("player_left", {"id": sid}, to=ROOM)
