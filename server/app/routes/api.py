import numpy as np
import matplotlib.pyplot as plt
import io

from . import routes
from .. import utils
from .. import models

import flask
from flask import json, Response, Flask, render_template, jsonify, request, make_response, send_file
from flask_api import status
import uuid
import time
import threading

from .events import socketio
import base64
from ..models.Database import Database
from ..models.Sessions import Session

import time
import math
import requests
import random
import logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# MY CODE
import seaborn as sns

# we need to log the state
# session id ==> ema position
# keep the state her
'''
key: session_id;
all_emas:
reported_emas: 
we need to use this to track the progress
'''

# 2 response handling mode
# repeat mode, which allows users to confirmation, or redo;
# add more, if users have more response to continue;
class ERRNO:
    NOT_REGISTERED_DEVICE = -1
    FINISH_ALL_SESSION = 0

state = utils.State.State()

# use the current response to find the next message
def get_next_message(device_id, session_id, response, input_method):
    '''
    get the device and session id, update the cache and get the next message meta data
    :return: positive number, the question id,
    '''
    assert device_id != None and session_id != None, "get message argument error!"

    res = utils.dynamo_connector.get_ema_topics_from_device_id(device_id)

    if res["ok"] != True:
        return ERRNO.NOT_REGISTERED_DEVICE, False

    ema_topic_ids = res["data"]["ema_topics"]
    res = state.get_curr_topic_and_question(session_id)

    # if this is the root question
    if res["ok"] != True:
        # hit the root message, we first fetch the ema topic, we need to add the disclaim message here
        init_topic_idx = 0
        next_ema_topic_id = ema_topic_ids[init_topic_idx]

        # it would keep hitting the false results when false trigger
        while state.is_topic_valid(next_ema_topic_id, device_id) == False:
            init_topic_idx += 1
            # might over-increasing
            if init_topic_idx >= len(ema_topic_ids):
                return ERRNO.FINISH_ALL_SESSION, False
            next_ema_topic_id = ema_topic_ids[init_topic_idx]

        if init_topic_idx >= len(ema_topic_ids):
            # upon finishing all question
            state.end_session(session_id)
            # when finish all topic
            return ERRNO.FINISH_ALL_SESSION, False

        # todo: we would add the topic id here.
        next_ema_topic = utils.dynamo_connector.get_ema_topic(next_ema_topic_id)
        state.add_topic_to_device(next_ema_topic_id, device_id)

        assert next_ema_topic["ok"] == True, "Not able to get the ema topic " + utils.util.get_linenumber()

        # from ema topics, we will fetch the next question id
        next_question_id = random.choice(next_ema_topic["data"]["root_questions"])

        # add to the cache
        state.create_and_add_session(session_id, next_ema_topic_id, next_question_id, True)

        return next_question_id, True # is root

    # if it is not the root message, then we will retrive data from the cache
    curr_topic_id = res["data"]["curr_topic"]
    curr_question_id = res["data"]["curr_question"]

    # todo: add topic id to the device
    # check the branching first
    curr_question = utils.dynamo_connector.get_ema_question(curr_question_id)
    assert curr_question["ok"] == True, "Not able to get the question id "
    condition_ids = curr_question["data"]["conditions"]

    # we want to find the next question id
    next_question_id = -1
    if len(condition_ids) == 0:
        # if there are no branching, then go through the first question of the next topics

        # move to the next topic index
        curr_topic_idx = ema_topic_ids.index(curr_topic_id)
        curr_topic_idx += 1

        while state.is_topic_valid(curr_topic_idx, device_id) == False:
            curr_topic_idx += 1

        if curr_topic_idx >= len(ema_topic_ids):
            # upon finishing all question
            state.end_session(session_id)

            # when finish all topic
            return ERRNO.FINISH_ALL_SESSION, False

        next_ema_topic_id = ema_topic_ids[curr_topic_idx]
        next_ema_topic = utils.dynamo_connector.get_ema_topic(next_ema_topic_id)

        assert next_ema_topic["ok"] == True, NotImplementedError("Not able to find the ema topic " + utils.util.get_linenumber())
        state.add_topic_to_device(next_ema_topic_id, device_id)


        next_question_id = random.choice(next_ema_topic["data"]["root_questions"])
        state.create_and_add_session(session_id, next_ema_topic_id, next_question_id, True)  # add to the cache

        return next_question_id, False
    else:
        # if there are branching, we need to find the "branch" that match the responses
        res = []
        for condition_id in condition_ids:
            condition = utils.dynamo_connector.get_ema_question_condition(condition_id)
            # process the condition
            # answer validator

            if utils.util.process_condition(condition["data"]["condition"], answer=response, input_method = input_method):
                res.append(condition["data"]["next_ema_question_node"])

        logging.info(res)
        # if none is satisfied, then we will get the next ema topics
        if len(res) == 0:
            curr_topic_idx = ema_topic_ids.index(curr_topic_id)
            curr_topic_idx += 1  # the next one might not be the true

            while state.is_topic_valid(curr_topic_idx, device_id) == False:
                curr_topic_idx += 1

            if curr_topic_idx >= len(ema_topic_ids):
                # upon finishing all question
                state.end_session(session_id)

                # when finish all topic
                return ERRNO.FINISH_ALL_SESSION, False

            next_ema_topic_id = ema_topic_ids[curr_topic_idx]
            next_ema_topic = utils.dynamo_connector.get_ema_topic(next_ema_topic_id)

            assert next_ema_topic["ok"] == True, NotImplementedError(
                "Not able to find the ema topic " + utils.util.get_linenumber())
            state.add_topic_to_device(next_ema_topic_id, device_id)

            next_question_id = random.choice(next_ema_topic["data"]["root_questions"])
            state.create_and_add_session(session_id, next_ema_topic_id, next_question_id, True)  # add to the cache

            return next_question_id, False

        next_question_id = random.choice(res)
        state.create_and_add_session(session_id, curr_topic_id, next_question_id, True) # did not change the topic

        return next_question_id, False


@routes.route('/api/v2/get_next_message', methods=["POST"])
def api_v2_get_next_message():
    # user id is only used for logging
    user_id = request.json['user_id']
    device_id = request.json['device_id']
    session_id = request.json['session_id']
    response = request.json["response"]
    input_method = request.json["input_method"]
    support_apl = request.json["support_apl"]

    # log the participants' speech
    utils.dynamo_connector.write_message(user_id=user_id, device_id=device_id, session_id=session_id,
                                         input=input_method, apl=support_apl, audio=str(response), source="USER")

    logging.info(f"user id: {user_id}, device_id: {device_id}, session_id: {session_id}, response: {str(response)}, "
                 f"input_method: {input_method}, support_apl: {support_apl}")

    logging.info(f"all state sessions: {state.get_sessions()}")
    logging.info(f"all state devices: {state.get_devices()}")
    res = state.get_curr_topic_and_question(session_id)
    logging.info(f"curr_topic_and_question: {res}")

    # if this is not the root question
    if res["ok"] == True:
        curr_question_id = res["data"]["curr_question"]
        # get the answer validator obj
        curr_question = utils.dynamo_connector.get_ema_question(curr_question_id)
        # get the answer schema
        answer = utils.dynamo_connector.get_answer(curr_question["data"]["answer"])
        answer_condition_data_fetching = answer["data"]["condition"]["data_fetching"]
        answer_condition_ret_condition = answer["data"]["condition"]["ret_condition"]
        answer_number_attempt = int(answer["data"]["number_of_attempt"])

        # only validate if it is below the number of attempt
        if res["data"]["curr_question_attempt_counter"] < answer_number_attempt:
            # process the answer and determine whether proceed or keep trying?
            validator_res = utils.util.process_condition(answer_condition_ret_condition,
                                                    date_fetching_code = answer_condition_data_fetching,
                                                    answer = response,
                                                    input_method = input_method)

            if validator_res != True:
                # repeat the question
                audio = utils.dynamo_connector.get_audio(curr_question["data"]["audio"])
                visual = utils.dynamo_connector.get_visual(curr_question["data"]["visual"])
                # add the attempt counter
                state.add_attempt_to_curr_question(session_id)

                if type(validator_res) == str and len(validator_res) > 0:

                    _ret = utils.util.get_apl_data(
                        visual["data"],
                        validator_res,
                        audio["data"]["audio_scripts"],
                        support_apl,
                        should_session_end=False)

                    utils.dynamo_connector.write_message(
                        user_id=user_id,
                        device_id=device_id,
                        session_id=session_id,
                        source="DEVICE",
                        apl=support_apl,
                        audio=_ret["speak"],
                        visual_heading=_ret["card_title"],
                        visual_subheading=_ret["card_content"]
                    )

                    return jsonify(_ret)
                else:
                    _ret = utils.util.get_apl_data(visual["data"],
                                                   "something is wrong, please try again",
                                                   audio["data"]["audio_scripts"],
                                                   support_apl, should_session_end=False)

                    utils.dynamo_connector.write_message(
                        user_id=user_id,
                        device_id=device_id,
                        session_id=session_id,
                        source="DEVICE",
                        apl=support_apl,
                        audio=_ret["speak"],
                        visual_heading=_ret["card_title"],
                        visual_subheading=_ret["card_content"]
                    )

                    return jsonify(_ret)

    # this is not the root question, but it is a long question, where responses are composed by multiple parts
    if res["ok"] == True and res["data"]["is_complete"] == False:
        # compare the current response, if it is not finish, then say the connection phrase
        curr_question_id = res["data"]["curr_question"]
        curr_question = utils.dynamo_connector.get_ema_question(curr_question_id)
        audio = utils.dynamo_connector.get_audio(curr_question["data"]["audio"])
        visual = utils.dynamo_connector.get_visual(curr_question["data"]["visual"])
        ending_phrases = audio["data"]["property"]["ending_phrases"]
        connection_phrases = audio["data"]["property"]["connection_phrases"]

        if response in ending_phrases:
            # we should enter the next question
            state.set_currention_completion_status(session_id, True) # set to complete
        else:
            # otherwise, we just need to return with the current responses
            # get the visual property
            # !!! PART 2 APL: go to get_apl_data() and change url to fectch graph !!!
            _ret = utils.util.get_apl_data(visual["data"], "", connection_phrases, support_apl, should_session_end=False)

            utils.dynamo_connector.write_message(
                user_id=user_id,
                device_id=device_id,
                session_id=session_id,
                source="DEVICE",
                apl=support_apl,
                audio=_ret["speak"],
                visual_heading=_ret["card_title"],
                visual_subheading=_ret["card_content"]
            )

            return jsonify(_ret)

    # when hit here, it means it is a brand new sessions, either it is root, or the false trigger from the users' side
    # current message finished find the next message, probably we should separate the root message
    next_question_id, is_root = get_next_message(device_id, session_id, response, input_method)

    print(f"next question id {next_question_id}, is root? {is_root}")

    # todo: separate the generate pre-question text;
    ack_msg = ""
    if is_root:
        ack_msg = "If this is an emergency, call 9-1-1!"
    else:
        ack_msg = random.choice(["Thanks!", "OK!", "Let's proceed to the next one!"])

    # check the exception
    if next_question_id == ERRNO.NOT_REGISTERED_DEVICE:

        _ret = utils.util.get_apl_data(
            {
                "type": "single_session",
                "property": {
                    "heading": "Your device has not been registered!",
                    "subheading": "Please contact the administrators!"
                }

            }, "", ["Your device has not been registered!"], support_apl, should_session_end=True)

        utils.dynamo_connector.write_message(
            user_id=user_id,
            device_id=device_id,
            session_id=session_id,
            source="DEVICE",
            apl=support_apl,
            audio=_ret["speak"],
            visual_heading=_ret["card_title"],
            visual_subheading=_ret["card_content"]
        )

        return jsonify(_ret)

    if next_question_id == ERRNO.FINISH_ALL_SESSION:
        _ret = utils.util.get_apl_data(
            {
                "type": "single_session",
                "property": {
                    "heading": "You have finished all questions.",
                    "subheading": "Have a nice day!"
                }

            }, ack_msg, ["You have finished all questions! Have a nice day!"],
            False, should_session_end=True)

        utils.dynamo_connector.write_message(
            user_id=user_id,
            device_id=device_id,
            session_id=session_id,
            source="DEVICE",
            apl=support_apl,
            audio=_ret["speak"],
            visual_heading=_ret["card_title"],
            visual_subheading=_ret["card_content"]
        )

        print(jsonify(_ret))

        return jsonify(_ret)


    next_question = utils.dynamo_connector.get_ema_question(next_question_id)
    assert next_question["ok"] == True, "not find the question"

    logging.info(f"next question: {next_question}")

    schedule_ids = next_question["data"]["schedules"]

    # find the one with correct schedule
    while utils.util.check_schedules(schedule_ids) == False:
        next_question_id, is_root = get_next_message(device_id, session_id, response, input_method)

        ack_msg = ""
        if is_root:
            ack_msg = "If this is emergency, call 9-1-1!"
        else:
            ack_msg = random.choice(["Thanks!", "OK!", "Let's proceed to the next one!"])

        # check the exception
        if next_question_id == ERRNO.NOT_REGISTERED_DEVICE:
            _ret = utils.util.get_apl_data(
                {
                    "type": "single_session",
                    "property": {
                        "heading": "Your device has not been registered!",
                        "subheading": "Please contact the administrators!"
                    }

                }, "", ["Your device has not been registered!"], False, should_session_end=True)

            utils.dynamo_connector.write_message(
                user_id=user_id,
                device_id=device_id,
                session_id=session_id,
                source="DEVICE",
                apl=support_apl,
                audio=_ret["speak"],
                visual_heading=_ret["card_title"],
                visual_subheading=_ret["card_content"]
            )

            return jsonify(_ret)

        if next_question_id == ERRNO.FINISH_ALL_SESSION:
            _ret = utils.util.get_apl_data(
                {
                    "type": "single_session",
                    "property": {
                        "heading": "You have finished all questions.",
                        "subheading": "Have a nice day!"
                    }

                }, "", ["You have finished all questions! Have a nice day!"],
                False, should_session_end=True)

            utils.dynamo_connector.write_message(
                user_id=user_id,
                device_id=device_id,
                session_id=session_id,
                source="DEVICE",
                apl=support_apl,
                audio=_ret["speak"],
                visual_heading=_ret["card_title"],
                visual_subheading=_ret["card_content"]
            )

            return jsonify(_ret)


        next_question = utils.dynamo_connector.get_ema_question(next_question_id)
        assert next_question["ok"] == True, "not find the question"

        schedule_ids = next_question["data"]["schedules"]

    audio_id = next_question["data"]["audio"]
    visual_id = next_question["data"]["visual"]


    audio, visual = utils.dynamo_connector.get_audio(audio_id), utils.dynamo_connector.get_visual(visual_id)
    assert audio["ok"] == True and visual["ok"] == True, "Not able to get the audio data"

    logging.info(f"audio: {audio}, visual: {visual}")

    # todo check the occurrence time
    # multi-session need to be handled separately, we need to set the completion status here
    if audio["data"]["type"] == "multiple_session":
        state.set_currention_completion_status(session_id, False)

    _ret = utils.util.get_apl_data(visual["data"], ack_msg, audio["data"]["audio_scripts"], support_apl)
    print(f"DEBUG:: return: {_ret}")

    utils.dynamo_connector.write_message(
        user_id=user_id,
        device_id=device_id,
        session_id=session_id,
        source="DEVICE",
        apl=support_apl,
        audio=_ret["speak"],
        visual_heading=_ret["card_title"],
        visual_subheading=_ret["card_content"]
    )

    return jsonify(_ret)


'''
return value should use the APL format
'''


# curl -v 127.0.0.1:443/return-file-small.png
@routes.route('/return-file-small.png')
def return_file_small():
    print('return file small')
    return send_file('../../figures/sleepquality.jpg', attachment_filename='sleepquality.jpg')


# curl -v 127.0.0.1:443/return-file-large.png
@routes.route('/return-file-large.png')
def return_file_large():
    print('return file large')
    return send_file('../../figures/sleepquality.jpg', attachment_filename='sleepquality.jpg')


@routes.route('/api/start_session', methods=["POST"])
def start_session():
    '''
    create the session states
    '''
    user_id = request.json['user_id']
    device_id = request.json['device_id']
    session_id = request.json['session_id']
    request_id = request.json['request_id']

    # todo: authenticate the users

    state[session_id] = {
            'completed': [],
            'current': None,
            'expire_s': time.time() + 3600
    }

#    print(state)

    return jsonify({
        "ok": True
    }), 200


@routes.route('/api/end_session', methods=["POST"])
def end_session():
    '''
    remove the session states
    '''
    user_id = request.json['user_id']
    device_id = request.json['device_id']
    session_id = request.json['session_id']
    request_id = request.json['request_id']

    # todo: authenticate the users
    # todo: we also want to log the timestamp

    if session_id in state:
        del state[session_id]

    return jsonify({
        "ok": True
    }), 200


@routes.route('/api/v2/debug/state', methods=["GET"])
def get_state():
    print("hello world")
    print(request)
    return jsonify({
        "ok": True,
        "state": state.get_sessions(),
        "devices": state.get_devices()
    }), 200


@routes.app_errorhandler(404)
def handle404(error):
    return jsonify({"ok": False, "error": "not found!"}), 404


@routes.app_errorhandler(405)
def handle404(error):
    return jsonify({"ok": False, "error": "methods are not allowed!"}), 405
