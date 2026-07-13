# Neon Racing Ultimate Ultra

One Flask app, one deployment: the game, the API, and multiplayer all live
together.

- `backend/app/static/index.html` — the game (Three.js, single file).
  Flask serves this directly at `/`.
- `backend/app/` — the API: accounts, cloud save, anti-cheat run
  validation, leaderboard, weekly challenges, and the multiplayer
  websocket (`backend/app/sockets.py`).

The game works fully offline as a guest with zero setup. To turn on cloud
accounts (login, cross-device save, real leaderboard), just deploy — no
separate frontend hosting, no CORS setup, no URLs to copy anywhere. The
game calls its own API at a relative path (`/api/...`), since Flask serves
both from the same origin.

## ▶ Play it — the one-click way

You only need **Python** installed (3.9+). Nothing else.

- **Windows:** double-click `PLAY.bat`
- **Mac / Linux:** double-click `play.sh` (or run `./play.sh` in a terminal)
- **Any OS, from a terminal:** `python play.py` (or `python3 play.py`)

That's it. The script installs any missing pieces automatically, sets up
the local database the first time, starts the server, and opens the game
in your browser. Leave the terminal window open while you play — closing
it stops the server. Press `CTRL+C` in that window to stop it manually.

## 🌐 Multiplayer

There's a **Multiplayer** toggle on the main menu. Turn it on before
hitting "Start Race" and you'll see everyone else who's currently
connected to the same server racing alongside you in real time (live
"ghost" cars + a small live-distance leaderboard). Turn it off to race
solo as before.

To race with friends, everyone just needs to open the same server address
in their browser:
- **Same computer / same Wi-Fi:** whoever runs `play.py` shares their
  local network address (the script prints it, or use the "Running on
  http://<your-ip>:5000" line) so friends on the same network can open it
  too.
- **Over the internet:** deploy the app (see below) and share the public
  URL — everyone who opens it and flips Multiplayer ON races together.

Multiplayer is a lightweight "ghost" model: each player still runs their
own local race (their own traffic, hits, and scoring), and the server
just relays where everyone else is so you can see them nearby. It's meant
for racing alongside friends, not as a cheat-proof competitive mode.

## Deploy (Render, free tier)

1. Push this whole `neon-racing` folder to a GitHub repo.
2. Go to https://render.com → New → Blueprint → connect that repo.
   Render reads `backend/render.yaml` and creates the web service *and*
   the free Postgres database automatically.
3. Once deployed, open the Render shell for the service and run once:
   ```
   python scripts/init_db.py
   ```
   This creates the database tables.
4. Open your Render URL (e.g. `https://racing-game-backend.onrender.com`)
   in a browser — that's the game, live, with accounts and multiplayer
   working. Anyone else who opens that same URL and turns Multiplayer ON
   races with you.

That's the whole setup. No editing any URLs inside the code.

## Running locally the manual way (equivalent to play.py, if you prefer)

```
cd backend
pip install -r requirements.txt
python scripts/init_db.py     # creates the local database the first time
python run.py
```
Then open http://localhost:5000 in a browser.

## Notes

- Weekly challenges aren't auto-created; seed one manually with
  `python scripts/seed_challenge.py` (edit the values in that file first),
  or build a small admin endpoint later.
- Coins can only ever be spent through `/api/save/purchase` (server
  computes the cost itself) and only ever earned through
  `/api/run/submit` (server validates distance/coins against elapsed
  time) — the client can never just POST an arbitrary coin total.
- Multiplayer state (who's online, their lane position/distance) is kept
  in memory only — it resets whenever the server restarts and is
  separate from the database, so it can never corrupt save data or
  leaderboard scores.
- If you ever DO want to host the game separately from the API (e.g. on
  GitHub Pages), copy `backend/app/static/index.html` out, change
  `const API_BASE = '/api';` near the top of its `<script>` block to your
  full backend URL (`https://your-backend.onrender.com/api`), and make
  sure `CORS_ORIGIN` in the backend's environment allows that origin.
  Multiplayer will also need that same backend URL — the socket connects
  to whatever origin the page is served from.
