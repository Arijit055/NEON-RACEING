from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO

# Single shared instances, initialized onto the app in create_app()
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
# threading async_mode = no eventlet/gevent needed, works with plain
# `python run.py` — that's what keeps local setup to "just have Python".
socketio = SocketIO(async_mode="threading")
