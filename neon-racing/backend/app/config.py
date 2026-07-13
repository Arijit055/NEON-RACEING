import os


class Config:
    # Render (and Heroku-style) DBs sometimes give postgres:// — SQLAlchemy needs postgresql://
    _raw_db_url = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    SQLALCHEMY_DATABASE_URI = _raw_db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24 * 30  # 30 days, in seconds

    # Flask-SocketIO needs this for its session cookie/signing (multiplayer)
    SECRET_KEY = os.environ.get("SECRET_KEY", JWT_SECRET_KEY)

    CORS_ORIGIN = os.environ.get("CORS_ORIGIN", "*")
