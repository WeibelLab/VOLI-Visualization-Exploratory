from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room
from flask import request
import time

socketio = SocketIO(engineio_logger=True, logger=True)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)

@socketio.on('connect')
def on_connect():
    print('=' * 20)
    print("connection::", request.headers)

#     time.sleep(2)
# # TODO: check this
#     socketio.emit('query', {
#         'data': {
#             'deviceId': "test",
#             'requestId': "test",
#             'sessionId': "test",
#             'query': "test"
#         }
#     })


@socketio.on('disconnect')
def on_disconnect():
    print("disconnection")

# Handles the default namespace
@socketio.on_error()
def error_handler(e):
    pass

# handles all namespaces without an explicit error handler
@socketio.on_error_default
def default_error_handler(e):
    pass

