"""
Flask extension instances.
Initialized here without an app so they can be imported anywhere
and registered later via app.init_app() pattern (Application Factory).
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
socketio = SocketIO()
