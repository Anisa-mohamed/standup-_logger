"""
Health and utility routes.

GET /api/health          — liveness probe for load balancers / Docker
GET /api/uploads/<path>  — serve uploaded files safely
"""
import os
from flask import Blueprint, send_from_directory, current_app
from app.utils.responses import success_response, error_response

health_bp = Blueprint('health', __name__, url_prefix='/api')


@health_bp.get('/health')
def health_check():
    """Simple health probe — returns 200 when the server is running."""
    return success_response(data={'status': 'healthy'}, message='Service is up')


@health_bp.get('/uploads/<path:filename>')
def serve_upload(filename: str):
    """
    Serve an uploaded file.

    Security: send_from_directory prevents path traversal by refusing
    paths that escape the upload directory.
    """
    upload_dir = current_app.config['UPLOAD_FOLDER']
    if not os.path.isfile(os.path.join(upload_dir, filename)):
        return error_response('File not found.', status_code=404)
    return send_from_directory(upload_dir, filename)
