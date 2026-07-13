"""Example: manually add a challenge for the current week.
Run: `python scripts/seed_challenge.py`
Edit the values below before running, or turn this into a real admin
endpoint later."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from app.extensions import db
from app.models import WeeklyChallenge
from app.utils import get_week_key

app = create_app()

with app.app_context():
    challenge = WeeklyChallenge(
        week_key=get_week_key(),
        challenge_type="distance",       # or 'coins_collected'
        target_value=5000,
        reward_coins=200,
        description="Travel 5000m total this week",
    )
    db.session.add(challenge)
    db.session.commit()
    print(f"✅ Seeded challenge {challenge.id} for week {challenge.week_key}")
