import boto3
import uuid
import time
# DO NOT CHANGE

class TABLE_NAME:
    DATA = "voli-data"
    USER = "voli-user"
    EMA = "voli-ema"
    MESSAGE = "voli-message"
    DEVICE = "voli-device"

dynamodb = boto3.client("dynamodb", region_name = "us-west-2")

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

def write_data(key, value, user_id, device_id):
    timestamp = int(time.time())  # unit of seconds

    return write_item({
        'id': {'S': str(uuid.uuid1())},
        'timestamp': {'N': str(timestamp)},
        'key': {'S': key},
        'value': {'N': value} if type(value) == int or type(value) == float else {'S': str(value)},
        'user': {'S': user_id},
        'device': {'S': device_id}
    }, TABLE_NAME.DATA)

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
        print(ex)
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

    print("message query response")

    print(response)

    if response['Count'] == 0:
        return None

    return response['Items'][0]

def get_next_message(curr_msg_id):
    response = dynamodb.query(
        TableName=TABLE_NAME.MESSAGE,
        KeyConditionExpression='prev_message_id = :prev_message_id',
        ExpressionAttributeValues = {
            ':prev_message_id': {'S': curr_msg_id},
        }
    )

    if response['Count'] == 0:
        # todo: couldn't find the next nessage
        return list()

    else:
        # todo: get the next nessage
        all_possible_responses = response['Items']  # a list of potential answers




        # todo: call container, execute and evaluate the results;



        # todo: change the structure for storing the corresponding answers;
        # todo: we need to be as flexible as possible;



        return "NOT IMPLEMENTED"


# for the testing only
# if __name__ == "__main__":
#
#
