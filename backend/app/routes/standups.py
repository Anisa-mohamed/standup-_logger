"""
Standup API Blueprint — /api/standups

Routes:
  POST   /api/standups          Submit a new standup
  GET    /api/standups          List all standups (newest first)
  GET    /api/standups/stats    Aggregated productivity stats
"""
import logging
from flask import Blueprint, request, send_from_directory, current_app
from marshmallow import ValidationError

from app.schemas import standup_input_schema, standup_list_schema, stats_schema
from app.services.standup_service import StandupService
from app.utils.responses import success_response, error_response
from app.extensions import socketio

logger = logging.getLogger(__name__)

standups_bp = Blueprint('standups', __name__, url_prefix='/api/standups')


@standups_bp.post('')
def create_standup():
    """
    POST /api/standups
    Accepts multipart/form-data.
    Returns the newly created standup.
    """
    # Parse form fields (multipart)
    form_data = {
        'author': request.form.get('author', ''),
        'yesterday': request.form.get('yesterday', ''),
        'today': request.form.get('today', ''),
        'blockers': request.form.get('blockers', ''),
    }

    # Validate input
    try:
        validated = standup_input_schema.load(form_data)
    except ValidationError as err:
        return error_response('Validation failed', errors=err.messages, status_code=422)

    # Optional file attachment
    file = request.files.get('attachment')

    try:
        post = StandupService.create_standup(validated, file_storage=file)
    except ValueError as err:
        # File type/size violation
        return error_response(str(err), status_code=400)
    except Exception as err:
        logger.exception('Unexpected error creating standup: %s', err)
        return error_response('Failed to save standup.', status_code=500)

    serialized = standup_list_schema.dump([post])[0]

    # Emit real-time event to all connected Socket.IO clients
    try:
        socketio.emit('new_standup', serialized, namespace='/feed')
    except Exception:
        pass  # Real-time failure must never break the HTTP response

    return success_response(data=serialized, message='Standup submitted!', status_code=201)


@standups_bp.get('')
def list_standups():
    """
    GET /api/standups
    Query params: limit (default 50), offset (default 0)
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 200)
        offset = int(request.args.get('offset', 0))
    except ValueError:
        return error_response('Invalid pagination parameters.', status_code=400)

    posts = StandupService.get_all_standups(limit=limit, offset=offset)
    serialized = standup_list_schema.dump(posts)
    return success_response(data=serialized)


@standups_bp.get('/stats')
def get_stats():
    """
    GET /api/standups/stats
    Returns aggregated productivity statistics for the last 7 days.
    """
    stats = StandupService.get_stats()
    return success_response(data=stats)
