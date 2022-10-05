import boto3
import uuid
import time, datetime
import pprint
# DO NOT CHANGE

class TABLE_NAME:
    DATA = "voli-data"
    USER = "voli-user"
    EMA = "voli-ema"
    MESSAGE = "voli-message"  # store the nodes
    DEVICE = "voli-device"
    ANSWERS = "voli-answers"  # store the edges

dynamodb = boto3.client("dynamodb", region_name = "us-west-2")

def get_ema_topics_from_device_id(device_id):
    response = dynamodb.query(
        TableName="DEVICE",
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'S': device_id}
        }
    )
    items = response["Items"]

    if len(items) != 1:
        return {
            "ok": False
        }

    return {
        "ok": True,
        "data": {
            "id": items[0]["id"]["S"],
            "ema_topics": items[0]["ema_topics"]["SS"]
        }
    }

    return True

def get_audio(audio_id):
    response = dynamodb.query(
        TableName="AUDIO",
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'S': audio_id}
        }
    )
    items = response["Items"]

    if len(items) != 1:
        return {
            "ok": False
        }

    # we also need to parse the property
    property = {}
    for key, value in items[0]["property"]["M"].items():
        if 'SS' in value:
            property[key] = value["SS"]
        elif "S" in value:
            property[key] = value["S"]

    return {
        "ok": True,
        "data": {
            "id": items[0]["id"]["S"],
            "audio_scripts": items[0]["audio_scripts"]["SS"],
            "type": items[0]["type"]["S"],
            "property": property
        }
    }

def get_visual(visual_id):
    response = dynamodb.query(
        TableName="VISUAL",
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'S': visual_id}
        }
    )
    items = response["Items"]

    if len(items) != 1:
        return {
            "ok": False
        }

    # we also need to parse the property
    property = {}
    for key, value in items[0]["property"]["M"].items():
        if 'SS' in value:
            property[key] = value["SS"]
        elif "S" in value:
            property[key] = value["S"]

    return {
        "ok": True,
        "data": {
            "id": items[0]["id"]["S"],
            "type": items[0]["type"]["S"],
            "property": property
            }
        }

def get_answer(answer_id):
    response = dynamodb.query(
        TableName="ANSWER",
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'S': answer_id}
        }
    )
    items = response["Items"]

    if len(items) != 1:
        return {
            "ok": False
        }

    return {
        "ok": True,
        "data": {
            "id": items[0]["id"]["S"],
            "condition": {
                "data_fetching": items[0]["condition"]["M"]["data_fetching"]["S"],
                "ret_condition": items[0]["condition"]["M"]["ret_condition"]["S"]
            },
            "number_of_attempt": items[0]["number_of_attempt"]["N"]
            }
        }

def get_schedule(schedule_id):
    response = dynamodb.query(
        TableName="SCHEDULE",
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'S': schedule_id}
        }
    )
    items = response["Items"]

    if len(items) != 1:
        return {
            "ok": False
        }

    # we also need to parse the property
    time_intervals = []
    for _interval_id in items[0]["time_intervals"]["SS"]:
        res = dynamodb.query(
            TableName="TIME_INTERVAL",
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={
                ':id': {'S': _interval_id}
            }
        )
        start = res["Items"][0]["start"]["S"]
        end = res["Items"][0]["end"]["S"]

        time_intervals.append([start, end])

    weekdays = []
    for _item in items[0]["weekdays"]["NS"]:
        weekdays.append(int(_item))

    return {
        "ok": True,
        "data": {
            "id": items[0]["id"]["S"],
            "weekdays": weekdays,
            "time_invervals": time_intervals
            }
        }

def get_visual_widget(widget_id):
    response = dynamodb.query(
        TableName="VISUAL_ELEMENTS",
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'S': widget_id}
        }
    )
    items = response["Items"]

    if len(items) != 1:
        return {
            "ok": False
        }

    return {
            "ok": True,
            "data": {
                "id": items[0]["id"]["S"],
                "type": items[0]["type"]["S"],
                "text": items[0]["text"]["S"],
                "value": items[0]["value"]["S"],
            }
        }

def get_ema_question(question_id):
    response = dynamodb.query(
        TableName="EMA_QUESTION_NODE",
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'S': question_id}
        }
    )
    items = response["Items"]

    if len(items) != 1:
        return {
            "ok": False
        }

    if "conditions" in items[0]:
        return {
            "ok": True,
            "data": {
                "id": items[0]["id"]["S"],
                "audio": items[0]["audio"]["S"],
                "visual": items[0]["visual"]["S"],
                "answer": items[0]["answer"]["S"],
                "conditions": items[0]["conditions"]["SS"], ## will cause expt
                "schedules": items[0]["schedules"]["SS"],
            }
        }
    else:
        return {
            "ok": True,
            "data": {
                "id": items[0]["id"]["S"],
                "audio": items[0]["audio"]["S"],
                "visual": items[0]["visual"]["S"],
                "answer": items[0]["answer"]["S"],
                "conditions": [], ## will cause expt
                "schedules": items[0]["schedules"]["SS"],
            }
        }

def get_ema_question_condition(condition_id):
    response = dynamodb.query(
        TableName="EMA_QUESTION_CONDITION",
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'S': condition_id}
        }
    )
    items = response["Items"]

    if len(items) != 1:
        return {
            "ok": False
        }

    return {
        "ok": True,
        "data": {
            "id": items[0]["id"]["S"],
            "condition": items[0]["condition"]["S"],
            "next_ema_question_node": items[0]["next_ema_question_node"]["S"]
        }
    }

def get_ema_topic(topic_id):
    response = dynamodb.query(
        TableName="EMA_TOPIC",
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues={
            ':id': {'S': topic_id}
        }
    )
    items = response["Items"]

    if len(items) != 1:
        return {
            "ok": False
        }

    return {
        "ok": True,
        "data": {
            "id": items[0]["id"]["S"],
            "root_questions": items[0]["root_questions"]["SS"],
        }
    }

    return True



# should not be called directly
def write_item(item, table):
    '''
    PRIVATE
    the table name need to make sure it is correct
    '''
    try:
        response = dynamodb.put_item(
            TableName = table,
            Item = item
        )

        return True
    except Exception as ex:
        print(ex)
        return False

def write_message(user_id="None",
               device_id="None",
               session_id="None",
               source="None",
               apl =None,
               audio ="None",
               visual_heading="None",
               visual_subheading="None",
               input="None"):
    '''
    :param user_id:
    :param device_id:
    :param session_id:
    :param request_id:
    :param epoch_ms:
    :param initiator:
    :param apl:
    :param value: the content being sent out, or the response that user said
    :return:
    '''

    epoch_ms = round(time.time() * 1e+3)
    timestamp_str = datetime.datetime.fromtimestamp(epoch_ms * 1e-3).isoformat()

    try:
        write_item({
            'id': {'S': str(round(time.time() * 1e+9))}, # use micro-sec level epoch for id
            'epoch_ms': {'N': str(epoch_ms)},
            'timestamp_str': {'S': timestamp_str},
            'user_id': {'S': user_id},
            'device_id': {'S': device_id},
            'session_id': {'S': session_id},
            'source': {'S': source},
            'apl': {'BOOL': apl},
            'input': {'S': input},
            'audio': {'S': audio},
            'visual_heading': {'S': visual_heading},
            'visual_subheading': {'S': visual_subheading}
        }, "MESSAGE")
    except Exception as ex:
        #        print(ex)
        return False


def read_data(key, user_id, window):
    '''
    window indicate number of data we want to read from now
    window is the length of the data in the unit of days
    '''
    # window to ms
    window_ms = window * 24 * 60 * 60 * 1000
    timestamp_end = int(time.time() * 1e+3)  # ms
    timestamp_start = timestamp_end - window_ms
    response = dynamodb.query(
        TableName = TABLE_NAME.DATA,
        KeyConditionExpression = 'user_id = :user_id AND key = :key AND timestamp BETWEEN :t_lower AND :t_upper',
        ExpressionAttributeValues = {
            ':user_id': {'S': user_id},
            ':key': {"S": key},
            ':t_lower' : {'N': timestamp_start},
            ':t_upper' : {'N': timestamp_end}
        }
    )

    return response['Items']

def write_user(user_id, devices):
    try:
        # write only when type is correct
        if type(user_id) == str and type(devices) == list:
            return write_item({
                'id': {'S': user_id},
                'devices': {'SS': devices}
            }, TABLE_NAME.USER)
        return False

    except Exception as ex:
#        print(ex)
        return False

def read_user(user_id):
    '''
    is it a real user?
    '''
    response = dynamodb.query(
        TableName = TABLE_NAME.USER,
        KeyConditionExpression = 'id = :id',
        ExpressionAttributeValues = {
            ':id': {'S': user_id}
        }
    )

    if response['Count'] == 0:
        return None

    return response['Items'][0] # fetch the first bean

def read_device(device_id):
    '''
    is it a real user?
    '''
    response = dynamodb.query(
        TableName = TABLE_NAME.DEVICE,
        KeyConditionExpression = 'id = :id',
        ExpressionAttributeValues = {
            ':id': {'S': device_id}
        }
    )

    print("=" * 10)
    print("device id: ", device_id)
    print("searched device id: ")
    print(response)

    if response['Count'] == 0:
        return None

    return response['Items'][0] # fetch the first bean

def validate_device(user_id, device_id):
    '''
    is it a valid device, check for every request, to prevent ddos
    '''
    user = read_user(user_id)

    # not found the user
    if user is None:
        return False

    # check the device affliations
    devices = user['devices']['SS']  # we only need the string set type

    try:
        if devices is not None and type(devices) == list:
            return device_id in devices
    except Exception as ex:
        print(ex)
        return False

# ema question related
def write_ema(question, answer_type, trigger):
    '''
    reminding time is another story
    :param question:
    :param answer_type:
    :param trigger:
    :return:

    regarding
    '''
    return write_item({
        'id': {'S': str(uuid.uuid1())},
        'question': {'S': question},
        'answer_type': answer_type,
        'trigger': {'S': trigger}
    }, TABLE_NAME.EMA)

def add_ema_to_user(user_id, ema_ids):
    '''
    operate on the user bean
    add list of ema's to a particular user
    :return:
    '''
    # type check
    if not (type(user_id) == str and type(ema_ids) == list):
        print("wrong type")
        return False

    # get the user
    user = read_user(user_id)

    # not found the user
    if user is None:
        return False

    # insert ema id inside the user bean
    user['emas'] = {'SS': ema_ids}

    return write_item(user, TABLE_NAME.USER)

def read_ema_from_user(user_id):
    '''
    get all emas indices from a specific user;
    and read the details of all emas related questions
    :return:
    '''
    user = read_user(user_id)

    if user is None:
        return list()

    if 'emas' not in user:
        return list()

    ema_ids = user['emas']

    emas = []
    for _id in ema_ids:
        # find the ema beans
        response = dynamodb.query(
            TableName=TABLE_NAME.EMA,
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={
                ':id': {'S': _id}
            }
        )

        emas.append(response['Items'][0])

    return emas

def get_root_message(device_id):

    print("get root message id: ", device_id)

    device = read_device(device_id)

    print("data");
    print(device)

    if device is None or 'root_message' not in device:
        return None

    root_msg_id = device['root_message']['S']

    print("root message id to be searched: ", root_msg_id)

    response = dynamodb.query(
        TableName=TABLE_NAME.MESSAGE,
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues = {
            ':id': {'S': root_msg_id},
        }
    )

    if response['Count'] == 0:
        return None

    return response['Items'][0]


def get_message(msg):

    msg_id = msg["data"]

    response = dynamodb.query(
        TableName=TABLE_NAME.MESSAGE,
        KeyConditionExpression='id = :id',
        ExpressionAttributeValues = {
            ':id': {'S': msg_id},
        }
    )

    if response['Count'] == 0:
        return None

    return response['Items'][0]

def get_next_message(curr_msg_id, curr_response):

    print("------------")
    print("current message id: ", curr_msg_id)


    # we can think the answer tabel as the edge
    response = dynamodb.scan(
        TableName=TABLE_NAME.ANSWERS,
        FilterExpression='prev_message_id = :prev_message_id',
        ExpressionAttributeValues = {
            ':prev_message_id': {'S': curr_msg_id},
        }
    )

    print("response from the search next message in Table: ", TABLE_NAME.ANSWERS)

    pprint.pprint(response)

    if response['Count'] == 0:
        # todo: couldn't find the next nessage
        return None

    else:
        # todo: get the next nessage
        all_possible_responses = response['Items']  # a list of potential answers

        # find the suitable one
        for _res in all_possible_responses:

            _condition = _res["condition"]['S']

            # todo: in current design, we only support the ALL condition, direct connect and only has one successor!!

            print("The condition being searched: ", _condition)
            print("current message: ", curr_response)
            if process_condition(_condition, answer=curr_response):
                next_msg_id = _res["next_message_id"]['S']

                # fetch the next message
                response = dynamodb.query(
                    TableName=TABLE_NAME.MESSAGE,
                    KeyConditionExpression='id = :id',
                    ExpressionAttributeValues={
                        ':id': {'S': next_msg_id},
                    })

                # TODO: think about it -- how to make it program dynamically
                print("the next response is ", response["Items"][0])
                return response['Items'][0]


 #           if _condition == "ALL":



        return None
        # todo: change the structure for storing the corresponding answers;
        # todo: we need to be as flexible as possible;

# for the testing only
# if __name__ == "__main__":
#
#

