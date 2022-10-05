from . import dynamo_connector
import time
import json

class State:

    '''
    sessions structure:
    current_topic, current_question
    '''
    DURATION_S = 3600

    def __init__(self):
        self.sessions = dict()

        # device id --> curr ema topics
        # each device maps to one latest question
        # if there are no sessions, then device-question mapping would be removed
        self.devices = dict() # device id --> question --> number of occurrence / timestamp

    def __contains__(self, session_id):
        return session_id in self.sessions

    def add_topic_to_device(self, topic_id, device_id):
        if device_id not in self.devices:
            self.devices[device_id] = {}

        self.devices[device_id][topic_id] = time.time()

    def is_topic_valid(self, topic_id, device_id):
        print(f"is_topic_valid::")
        print(f"topic_id: {topic_id}")
        print(f"device_id: {device_id}")
        print(f"devices: {self.devices}")
        print(f"-" * 10)

        if device_id not in self.devices:
            return True

        if device_id in self.devices:
            if topic_id not in self.devices[device_id]:
                return True

            _timestamp = self.devices[device_id][topic_id]
            if time.time() - _timestamp > 3600:
                return True

        return False

    def get_sessions(self):
        return self.sessions

    def get_devices(self):
        return self.devices

    def add_attempt_to_curr_question(self, session_id):
        if session_id in self.sessions:
            self.sessions[session_id]["curr_question_attempt_counter"] += 1

    def create_and_add_session(self, session_id, curr_topic_id, curr_question_id, is_complete):
        if session_id not in self.sessions:
            # this is the first time, so we should create a new session and give the root msg;
            self.sessions[session_id] = {"expiration": time.time() + State.DURATION_S}
        else:
            self.sessions[session_id]["expiration"] = time.time() + State.DURATION_S

        self.sessions[session_id]["curr_topic"] = curr_topic_id
        self.sessions[session_id]["curr_question"] = curr_question_id
        self.sessions[session_id]["is_complete"] = is_complete
        self.sessions[session_id]["curr_question_attempt_counter"] = 0

    def set_currention_completion_status(self, session_id, status):
        if session_id in self.sessions:
            self.sessions[session_id]["is_complete"] = status

    def end_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def get_curr_topic_and_question(self, session_id):
        if session_id not in self.sessions:
            return {
                "ok": False   # not found the question in the state
            }
        else:
            return {
                "ok": True,
                "data": {
                    "curr_topic": self.sessions[session_id]["curr_topic"],
                    "curr_question": self.sessions[session_id]["curr_question"],
                    "is_complete": self.sessions[session_id]["is_complete"],
                    "curr_question_attempt_counter": self.sessions[session_id]["curr_question_attempt_counter"]
                }
            }


