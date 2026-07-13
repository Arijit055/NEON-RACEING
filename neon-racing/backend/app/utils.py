from datetime import datetime, timezone


def get_week_key(dt=None):
    """ISO week key, e.g. '2026-W28'. Must match getWeekKey() in index.html
    so the frontend's local weekly-leaderboard fallback and the backend
    always agree on which week a score belongs to."""
    dt = dt or datetime.now(timezone.utc)
    iso_year, iso_week, _ = dt.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"
