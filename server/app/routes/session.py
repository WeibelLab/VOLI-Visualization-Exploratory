from . import routes
from .. import utils
from .. import models

import flask
from flask import json, Response, Flask, render_template, jsonify, request, make_response
from flask_api import status
import uuid
import time
import threading

from flask_socketio import emit, join_room, leave_room
from .events import socketio
import base64
from ..models.Database import Database
from ..models.Sessions import Session

import time
import math
import requests

db = Database()

# TODO: for the debugging only
@routes.route('/api/debug/sessions/print', methods=["GET"])
def get_all_sessions():
    return jsonify(Session.get_json()), 200

@routes.route('/api/sessions/get_metrics', methods=["POST"])
def get_non_reporting_metrics_prompt():
    if not all(key in request.json for key in ("user_id", "device_id", "session_id")):
        return jsonify({
            "ok": False,
            "message": "required field is none"
        }), status.HTTP_200_OK

    user_id = request.json["user_id"]
    device_id = request.json["device_id"]
    session_id = request.json["session_id"]

    # using the user_id to find out what to report
    user = db.get_user({"user_id": user_id})
    if user is None:
        return jsonify({"ok": False, "error": "user not found"}), 404

    all_health_data = list(user['healthdata'].values())

    # using the session id to find out what has been reported
    # we must ensure the session id is in the pools
    if not session_id in Session.session_pools:
        return jsonify({
            "ok": False,
            "message": "Invalid session"
        }), status.HTTP_200_OK

    session = Session.session_pools[session_id]
    reported_items = []
    for item in session.reported_metrics:
        reported_items.append(item["name"])

    # loop through all the listed data and removed the one that has been reported
    not_reported_metric = []
    for item in all_health_data:
        if item not in reported_items:
            not_reported_metric.append(item)

    return jsonify({
        "ok": True,
        "list": not_reported_metric,
        "speech": ', '.join(not_reported_metric)
    })




'''
we have three reporting phases in total:
- metric phase: metric reporting
- value phase: value confirmation
- results phase: results confirmations

We use the session to report the guidance and non-guidance scenario
'''

'''
check with the schema and make sure the data format is correct
'''
@routes.route('/api/sessions/metric_reporting', methods=["POST"])
def validate_reported_value():
    # the data will be directly posted from the voice flow

    # make sure the data is correct
    err = db.isDeviceValid(request)
    if err:
        return err

    if not all(key in request.json for key in ("user_id", "device_id", "session_id", "data")):
        return jsonify({
            "ok": False,
            "message": "required field is none"
        }), status.HTTP_200_OK

    user_id = request.json["user_id"]
    device_id = request.json["device_id"]
    session_id = request.json["session_id"]

    # the format of the data is the predefined schema
    data = request.json["data"]

    # fetch the session using session id, from session pool.
    if not session_id in Session.session_pools:
        return jsonify({
            "ok": False,
            "message": "Invalid session"
        }), status.HTTP_200_OK

    # get the session and parse error message
    session = Session.session_pools[session_id]
    reporting_metric = session.reporting_metric   # get the metric that is currently being reported

    # exit if the reporting metric is none
    if not reporting_metric:
        return jsonify({
            "ok": False,
            "message": "no current reporting metric found in the session"
        }), status.HTTP_200_OK

    # if the session has been found, then check the data format
    # here we need to check the correctnes of the data and parse all variables
    # return check contains: ok: flag;
    # if ok is false then  return a message;
    # otherwise return the list of data schema
    check = utils.util.dataCheck(data, reporting_metric)

    # if checking passed, then add it to the session pool
    # reporting metrics cannot be none
    # TODO: reporting metrics should be pulled out from the state memory, not expectingg user report it
    # but what kind of data can it be?? ["key", "value", "metrics"], note that key is not the reporting metrics
    if check["ok"]:
        session.reported_metrics.append(dict({
            "name": reporting_metric,
            "data": check["data"]   # array of all quantity under a particular reported metrics
        }))

    # if ok is true, then the return value contains the list of parsed data
    # other wise the returned value contains the error messages
    return jsonify(check), status.HTTP_200_OK  # ok and message (if not ok)

'''
generate the confirmation prompt, confirmation is mapping to a particular reporting metrics
'''
@routes.route('/api/sessions/prompt/confirmation', methods=["POST"])
def get_confirmation_prompt():
    # make sure the data is correct
    err = db.isDeviceValid(request)
    if err:
        return err

    if not all(key in request.json for key in ("user_id", "device_id", "session_id")):
        return jsonify({
            "ok": False,
            "message": "required field is none"
        }), status.HTTP_200_OK

    user_id = request.json["user_id"]
    device_id = request.json["device_id"]
    session_id = request.json["session_id"]

    # fetch the session using session id, from session pool.
    if not session_id in Session.session_pools:
        return jsonify({
            "ok": False,
            "message": "Invalid session"
        }), status.HTTP_200_OK

    # get the session and parse error message
    session = Session.session_pools[session_id]
    reporting_metric = session.reporting_metric   # get the metric that is currently being reported

    # loop through the session data pool and see the correct reported value
    for metric in session.reported_metrics:
        if metric["name"] == reporting_metric:
            # assemble message here
            msg = []
            for item in metric["data"]:
                msg.append(utils.util.get_message(item))
            speech = ' and '.join(msg)
            return jsonify({
                "ok": True,
                "message": speech
            }), 200

    # not founded the reporting metrics inside the session
    # then set the reporting metrics back to normal
    session.reporting_metric = None

    return jsonify({
        "ok": False,
        "message": "Did not find the data"
    }), 200

'''
delete the session upon the conversation ends
'''
@routes.route('/api/sessions/delete', methods=["POST"])
def delete_session():
    # make sure the data is correct
    err = db.isDeviceValid(request)
    if err:
        return err

    if not all(key in request.json for key in ("user_id", "device_id", "session_id")):
        return jsonify({
            "ok": False,
            "message": "required field is none"
        }), status.HTTP_200_OK

    user_id = request.json["user_id"]
    device_id = request.json["device_id"]
    session_id = request.json["session_id"]

    # fetch the session using session id, from session pool.
    if not session_id in Session.session_pools:
        return jsonify({
            "ok": True
        }), status.HTTP_200_OK

    del Session.session_pools[session_id]

    return jsonify({
        "ok": True
    }), 200

'''
create a new session upon the conversation starts 
'''
@routes.route('/api/sessions/create', methods=["POST"])
def create_session():
    # make sure the data is correct
    err = db.isDeviceValid(request)
    if err:
        return err

    if not all(key in request.json for key in ("user_id", "device_id", "session_id")):
        return jsonify({
            "ok": False,
            "message": "required field is none"
        }), status.HTTP_200_OK

    user_id = request.json["user_id"]
    device_id = request.json["device_id"]
    session_id = request.json["session_id"]

    Session.session_pools[session_id] = Session(device_id, user_id)
    return jsonify({
        "ok": True
    }), status.HTTP_200_OK

'''
set the reporting_metric in the metric reporting phase
'''
@routes.route('/api/sessions/set_reporting_metric', methods=["POST"])
def set_reporting_metric():
    # make sure the data is correct
    err = db.isDeviceValid(request)
    if err:
        return err

    if not all(key in request.json for key in ("user_id", "device_id", "session_id", "metric")):
        return jsonify({
            "ok": False,
            "message": "required field is none"
        }), status.HTTP_200_OK

    user_id = request.json["user_id"]
    device_id = request.json["device_id"]
    session_id = request.json["session_id"]

    reporting_metric = request.json["metric"] # a string

    # fetch the session using session id, from session pool.
    if not session_id in Session.session_pools:
       return jsonify({
            "ok": False,
            "message": "not found the session"
        }), status.HTTP_200_OK

    # if fetched the session
    session = Session.session_pools[session_id]

    # set the reporting metric
    session.reporting_metric = reporting_metric

    return jsonify({
        "ok": True
    }), status.HTTP_200_OK

