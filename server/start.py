#!/bin/env python
# from gevent import monkey
# monkey.patch_all()

import sys
sys.path.append('/home/ubuntu/.local/lib/python3.6/site-packages')

import os
import flask
import inspect

from app import create_app
from app.routes.events import socketio

# from OpenSSL import SSL
import ssl

# DO NOT CHANGE
context = ('/etc/letsencrypt/live/voli-test.chen-chen.me/fullchain.pem', '/etc/letsencrypt/live/voli-test.chen-chen.me/privkey.pem')

app = create_app()

# create the socket io
if __name__ == "__main__":
	# socketio.run(app, debug=True)
	# todo: enable https for the secure communications
	# app.run(port=443, debug=True, threaded=True, host='0.0.0.0')
	# app.run(port=443, host='0.0.0.0')
	app.run(port=443, host='0.0.0.0', ssl_context=context)