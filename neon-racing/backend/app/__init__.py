from flask import Flask, send_from_directory

from .config import Config
from .extensions import db, jwt, cors, socketio


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="")
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGIN"]}})
    socketio.init_app(app, cors_allowed_origins=app.config["CORS_ORIGIN"])

    from .sockets import register_socket_handlers
    register_socket_handlers(socketio)

    from .routes.auth import auth_bp
    from .routes.save import save_bp
    from .routes.run import run_bp
    from .routes.challenges import challenges_bp
    from .routes.leaderboard import leaderboard_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(save_bp, url_prefix="/api/save")
    app.register_blueprint(run_bp, url_prefix="/api/run")
    app.register_blueprint(challenges_bp, url_prefix="/api/challenges")
    app.register_blueprint(leaderboard_bp, url_prefix="/api/leaderboard")

    # models are imported (transitively, via the blueprints above) by this point,
    # so SQLAlchemy's metadata now knows about every table and can create them
    with app.app_context():
        db.create_all()

    @app.route("/health")
    def health():
        # Render's health check hits this — without it Render may mark the service unhealthy
        return {"status": "ok"}

    @app.route("/")
    def index():
        # Serves the game itself (app/static/index.html) — same origin as the
        # API, so no CORS setup or separate hosting is needed.
        return send_from_directory(app.static_folder, "index.html")

    return app
