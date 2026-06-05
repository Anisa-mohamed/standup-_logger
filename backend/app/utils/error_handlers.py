"""
Centralized error handling.
Registered on the app so every blueprint inherits them.
All errors return a consistent JSON envelope.
"""
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'success': False, 'message': str(e), 'data': None}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'message': 'Resource not found.', 'data': None}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'success': False, 'message': 'Method not allowed.', 'data': None}), 405

    @app.errorhandler(413)
    def request_too_large(e):
        return jsonify({
            'success': False,
            'message': 'File too large. Maximum size is 5 MB.',
            'data': None,
        }), 413

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception('Internal server error: %s', e)
        return jsonify({
            'success': False,
            'message': 'Internal server error. Please try again later.',
            'data': None,
        }), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({'success': False, 'message': e.description, 'data': None}), e.code
