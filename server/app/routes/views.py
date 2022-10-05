from . import routes
import flask
from flask import Response, Flask, render_template
from flask_api import status
from flask import request
import uuid
import time
import threading
from flask import jsonify

import requests

@routes.route('/', methods=['GET'])
def home():
    return jsonify({'ok': True}), status.HTTP_200_OK
    #	WOLFRAME_APP_ID = "1234567"
#	return render_template('home.html', WOLFRAME_APP_ID=WOLFRAME_APP_ID), status.HTTP_200_OK

