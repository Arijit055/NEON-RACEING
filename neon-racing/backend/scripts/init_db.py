"""Run once to create all tables: `python scripts/init_db.py`
For real schema changes later, switch to Flask-Migrate instead of re-running this."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Tables created.")
