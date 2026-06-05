"""
Application Factory Pattern.

Benefits:
- Multiple app instances (e.g. testing) without globals
- Extensions initialized after app configuration is known
- Clean circular-import prevention via extensions/__init__.py
"""
import os
import logging
from flask import Flask, send_from_directory

from app.config.settings import get_config
from app.extensions import db, migrate, cors, socketio
from app.utils.error_handlers import register_error_handlers


def create_app(config_class=None) -> Flask:
    static_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'dist')
    )
    flask_app = Flask(__name__, instance_relative_config=False, static_folder=None)
    flask_app.config['SPA_STATIC_FOLDER'] = static_folder

    # --- Configuration ---
    cfg = config_class or get_config()
    flask_app.config.from_object(cfg)

    # Ensure upload directory exists
    os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --- Logging ---
    logging.basicConfig(
        level=logging.DEBUG if flask_app.config.get('DEBUG') else logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s — %(message)s',
    )

    # --- Extensions ---
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    cors.init_app(flask_app, resources={r'/api/*': {'origins': flask_app.config['CORS_ORIGINS']}})
    socketio.init_app(
        flask_app,
        cors_allowed_origins=flask_app.config['CORS_ORIGINS'],
        async_mode='threading',  # Works on Python 3.14 and Windows; no eventlet needed
        logger=False,
        engineio_logger=False,
    )

    # --- Blueprints ---
    from app.routes.standups import standups_bp
    from app.routes.health import health_bp
    flask_app.register_blueprint(standups_bp)
    flask_app.register_blueprint(health_bp)

    # --- Socket.IO handlers (imported for side-effects) ---
    import app.sockets  # noqa: F401

    # --- Error handlers ---
    register_error_handlers(flask_app)

    # --- Single-page app support ---
    @flask_app.route('/', defaults={'path': ''})
    @flask_app.route('/<path:path>')
    def serve_spa(path):
        if path.startswith('api') or path.startswith('socket.io'):
            return ('', 404)

        static_folder = flask_app.config['SPA_STATIC_FOLDER']
        file_path = os.path.join(static_folder, path)
        if path and os.path.exists(file_path):
            return send_from_directory(static_folder, path)
        return send_from_directory(static_folder, 'index.html')

    flask_app.logger.info('Team Standup Logger started. ENV=%s', os.environ.get('FLASK_ENV', 'development'))
    return flask_app
