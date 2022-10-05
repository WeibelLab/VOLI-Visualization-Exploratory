import time
import csv
import time

DEFAULT_SAVE_INTERVAL = 10.  # in s

class Logger:

    def log(request):
        session_id = request['sessions_id']
        user_id = request['user_id']
        user_name = request['user_name']
        platform = request['platform']
        speech_timestamp = request['timestamp']
        speech = request['speech']
        source = request['source']
        log_timestamp = str(int(time.time()))

        # we use the user name as the file name
        file = open(user_name, mode="at", newline='')
        csvwriter = csv.writer(file, delimiter=",")

        csvwriter.writerow((session_id, user_id, user_name, platform, speech_timestamp, speech, source, log_timestamp))
        file.flush()
        # whether need to close??

