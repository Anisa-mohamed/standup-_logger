"""
Entry point for development server.

Production should use:
    gunicorn -w 4 run:app

Note: We use threading async_mode (not eventlet) for broad Python 3.12+/3.14
compatibility and Windows support. For high-concurrency production use, you
can switch to gevent by installing gevent and changing async_mode in app/__init__.py.
"""
from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', False),
        allow_unsafe_werkzeug=True,  # Required when using threading mode in dev
    )
