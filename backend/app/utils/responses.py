"""
Standardized JSON response helpers.

All API responses follow the envelope:
{
    "success": true | false,
    "data": { ... } | null,
    "message": "...",
    "errors": { ... } | null   # only on validation failures
}
"""
from flask import jsonify


def success_response(data=None, message='OK', status_code=200):
    return jsonify({
        'success': True,
        'message': message,
        'data': data,
    }), status_code


def error_response(message='An error occurred', errors=None, status_code=400):
    body = {
        'success': False,
        'message': message,
        'data': None,
    }
    if errors:
        body['errors'] = errors
    return jsonify(body), status_code
