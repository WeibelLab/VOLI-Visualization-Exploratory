from pymongo import MongoClient
from flask import jsonify

class Database:
    HOST = "localhost"
    PORT = 27017

    def __init__(self):
        try:
            self.client = MongoClient("localhost", 27017)
            self.voli = self.client.voli
        except Exception as ex:
            print(str(ex))
            print("get database error")

    def get_devices(self):
        # get the collections
        devices = self.voli.devices
        return devices.find_one()

    def get_user(self, condition):
        users = self.voli.users
        user = users.find_one(condition)
        return user

    def get_device(self, condition):
        devices = self.voli.devices
        device = devices.find_one(condition)
        return device

    def write_messages(self, request):
        session_id = request['session_id']
        # request_id = request['request_id']
        user_id = request['user_id']
        timestamp = request['timestamp']
        content = request['speech']
        source = request['source']

        messages = self.voli.messages
        messages.insert_one({
            "timestamp": timestamp,
            # "request_id": request_id,
            "session_id": session_id,
            "source": source,
            "content": content,
            "user_id": user_id
        })

    def write_heathdata(self, request):
        user_id = request["user_id"]
        timestamp = request["timestamp"]
        data = request["data"]
        healthdata = self.voli.vital_signals

        # for item in data:
        #     # post to the db
        #     print(item)
        healthdata.insert_one({
            "user_id": user_id,
            "timestamp": timestamp,
            "data": data
        })


    # TODO: get the error code
    def isDeviceValid(self, request):

        device_id = request.args.get("device_id")
        print("GET request: ", device_id)
        if not device_id or len(device_id) == 0:
            device_id = None

        try:
            device_id = request.json["device_id"]
            print("POST request: ", device_id)
        except Exception as ex:
            pass

        # if not found the valid device id
        if not device_id:
            return jsonify({
                "ok": False,
                "error": "invalid request",
            }), 403


        # print device id and user id

        query = self.voli.devices.find_one({"device_id": device_id})

        if not query:
            return jsonify({
                "ok": False,
                "error": "invalid devices",
            }), 403

        return None

