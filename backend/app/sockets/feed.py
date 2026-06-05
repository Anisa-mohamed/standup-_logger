"""
Socket.IO namespace: /feed

Events emitted by server → client:
  new_standup   payload: serialized StandupPost dict

Events received from client:
  connect       — logs connection
  disconnect    — logs disconnection
  request_feed  — client requests latest 10 standups on connect

Design note: the /feed namespace keeps standup traffic isolated
from any future namespaces (e.g. /notifications).
"""
import logging
from flask_socketio import emit, join_room

from app.extensions import socketio
from app.services.standup_service import StandupService
from app.schemas import standup_list_schema

logger = logging.getLogger(__name__)


@socketio.on('connect', namespace='/feed')
def on_connect():
    logger.info('Socket.IO client connected to /feed')
    emit('connected', {'message': 'Connected to standup feed.'})


@socketio.on('disconnect', namespace='/feed')
def on_disconnect():
    logger.info('Socket.IO client disconnected from /feed')


@socketio.on('request_feed', namespace='/feed')
def on_request_feed():
    """Send the 10 most recent standups to a newly connected client."""
    posts = StandupService.get_all_standups(limit=10)
    serialized = standup_list_schema.dump(posts)
    emit('feed_snapshot', serialized)
