import time

class Session:

    # session_id --> Session
    session_pools = dict()

    def __init__(self, deviceId, userId):
        self.deviceId = deviceId
        self.userId = userId

        self.timestamp = time.time()  # each session will be cleaned up after a fixed period

        self.reported_metrics = []   # all data to be reported under this session
        self.reporting_metric = None

    def __str__(self):
        session_id = "session id: " + self.sessionId
        # device_id = "device id: " + self.deviceId
        # user_id = "user id: " + self.userId

        n_metrics = "number of metrics " + len(self.reported_metrics)

        return session_id + " " + n_metrics + "\n"

    @staticmethod
    def get_json():
        res = {}
        for id, session in Session.session_pools.items():
            res[id] = {
                "device_id": session.deviceId,
                "user_id": session.userId,
                "timestamp": session.timestamp,
                "reporting_metrics": session.reporting_metric,
                "reported_metrics": session.reported_metrics  # contained all data under each reporting metrics
            }

        return res

    @staticmethod
    def all():
        '''
        print all sessions
        :return:
        '''
        print("********** All Sessions ***********")
        for session in Session.session_pools:
            print(session)


