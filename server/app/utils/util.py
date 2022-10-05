from inspect import currentframe
if __name__ != '__main__':
    from . import dynamo_connector
import random
import time
import sys
import os
import datetime

def check_schedules(schedule_ids):
    for id in schedule_ids:
        if check_schedule(id):
            return True
    return False

def check_schedule(schedule_id):
    now = datetime.datetime
    weekday = now.today().weekday()  # 0, 1, 2, 3, 4, 5, 6
    hour = now.now().hour
    min = now.now().minute
    second = now.now().second

    print(f"Check schedule::\nweekday: {weekday}, hour: {hour}, min: {min}, second: {second}")

    # get the schedule
    res = dynamo_connector.get_schedule(schedule_id)

    schedule_weekdays = res["data"]["weekdays"]
    schedule_time_intervals = res["data"]["time_invervals"]

    print(f"scheduled week days: {schedule_weekdays}, and time intervals: {schedule_time_intervals}")

    # check the week day
    if weekday not in schedule_weekdays:
        return False

    # check each of intervals
    for interval in schedule_time_intervals:
        start_hour, start_min, start_sec = interval[0].split(":")
        end_hour, end_min, end_sec = interval[1].split(":")

        if int(start_hour) <= hour <= int(end_hour) and int(start_min) <= min <= int(end_min) and int(start_sec) <= \
                second <= int(end_sec):
            return True

    return False

def fork_and_exec(code_str, result_key = "result"):
    import multiprocessing

    def worker(code_str, ret_dict):
        exec(code_str, globals(), ret_dict)

    manager = multiprocessing.Manager()
    ret_dict = manager.dict()
    p = multiprocessing.Process(target = worker, args=(code_str, ret_dict))
    p.start()
    p.join()  # wait to join

    assert result_key in ret_dict, "the result key is not in the return"

    return ret_dict[result_key]

# we need to simplify the routine for processing the condition
def process_condition (condition_code, date_fetching_code = "", answer = None, input_method = "SPEECH"):
    '''
    the reflective code can be thought as the data fetching code and the condition justification
    input: answer. the answer can be in different type
    processing: data fetching;
    output: result;
    '''

    assert type(condition_code) == str and type(date_fetching_code) == str, "wrong input type"
    assert type(input_method) == str

    print('=' * 20)
    print(f"condition code: {condition_code}")
    print(f"data fetching code: {date_fetching_code}")
    print(f"response: {answer}, answer type: {type(answer)}")

    try:
        # if there are no answer input
        if answer == None:
            code = f'{date_fetching_code}\nresult = ({condition_code})'

        # in the input answer type is string
        elif type(answer) == str:
            code = f'_answer_ = "{answer}"\n_input_method_="{input_method}"\n{date_fetching_code}\nresult = ' \
                   f'({condition_code})'

        elif type(answer) == int:
            code = f'_answer_ = int({answer})\n_input_method_="{input_method}"\n{date_fetching_code}\nresult = ' \
                   f'({condition_code})'

        elif type(answer) == float:
            code = f'_answer_ = float({answer})\n_input_method_="{input_method}"\n{date_fetching_code}\nresult = ' \
                   f'({condition_code})'

        elif type(answer) == bool:
            code = f'_answer_ = bool({answer})\n_input_method_="{input_method}"\n{date_fetching_code}\nresult = ' \
                   f'({condition_code})'

        else:
            raise Exception("Not implemented")

        print(f"final code to be executed: \n*****\n{code}")
        result = fork_and_exec(code)
        print(f"code conditioning result: {result}")
        print(f"=" * 20)
        return result
    except Exception as ex:
        return False  # for all other case

def get_apl_data(visual, ack, audio_scripts, support_apl, should_session_end = False):

    print(f"get_apl_data: {visual}, ack: {ack}, audio_scripts: {audio_scripts}, support_apl: {support_apl}")

    audio_script = random.choice(audio_scripts)   # select a random audio script

    visual_type = visual["type"]
    visual_property = visual["property"]

    # replace the visual property heading
    if visual_property["heading"] == "_audio_":
        visual_property["heading"] = audio_script

    print(f"---")
    print(f"visual property: {visual_property}, visual type: {visual_type}")

    if support_apl == True and (visual_type == "number_buttons" or visual_type == "boolean"):
        datasources = {
            "buttonExampleData": {
                "heading": visual_property["heading"],
                "subheading": visual_property["subheading"],
                "buttons": []
            }
        }

        buttons = visual_property["buttons"]
        for id in buttons:
            res = dynamo_connector.get_visual_widget(id)
            assert res["ok"] == True, "not found the button"
            datasources["buttonExampleData"]["buttons"].append({
                "buttonText": res["data"]["text"],
                "id": res["data"]["value"], # use the value as the id
                "buttonStyle": "outlined"
            })

        return {
            "should_session_end": should_session_end,
            "speak": ack + " " + audio_script,
            "reprompt": audio_script,
            "card_title": visual_property["heading"],
            "card_content": visual_property["subheading"],
            "addDirective": {
                "type": 'Alexa.Presentation.APL.RenderDocument',
                "document": {
                    "type": "APL",
                    "version": "1.5",
                    "theme": "dark",
                    "import": [
                        {
                            "name": "alexa-layouts",
                            "version": "1.2.0"
                        }
                    ],
                    "layouts": {
                        "ButtonRow": {
                            "parameters": [
                                {
                                    "name": "buttons",
                                    "type": "array"
                                },
                                {
                                    "name": "touchForwardSetting",
                                    "type": "boolean"
                                }
                            ],
                            "item": [
                                {
                                    "when": "${@viewportProfile != @hubRoundSmall}",
                                    "type": "Sequence",
                                    "width": "100%",
                                    "scrollDirection": "horizontal",
                                    "alignSelf": "center",
                                    "data": "${buttons}",
                                    "items": [
                                        {
                                            "type": "AlexaButton",
                                            "buttonText": "${data.buttonText}",
                                            "id": "${data.id}",
                                            "buttonStyle": "${data.buttonStyle}",
                                            "touchForward": "${touchForwardSetting}",
                                            "primaryAction": {
                                                "type": "SendEvent",
                                                "arguments": [
                                                    "AlexaButton"
                                                ]
                                            }
                                        }
                                    ]
                                },
                                {
                                    "when": "${@viewportProfile == @hubRoundSmall}",
                                    "type": "Sequence",
                                    "width": "100%",
                                    "scrollDirection": "vertical",
                                    "alignSelf": "center",
                                    "data": "${buttons}",
                                    "items": [
                                        {
                                            "type": "AlexaButton",
                                            "buttonText": "${data.buttonText}",
                                            "id": "${data.id}",
                                            "buttonStyle": "${data.buttonStyle}",
                                            "touchForward": "${touchForwardSetting}",
                                            "primaryAction": {
                                                "type": "SendEvent",
                                                "arguments": [
                                                    "AlexaButton"
                                                ]
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    },
                    "mainTemplate": {
                        "parameters": [
                            "buttonExampleData"
                        ],
                        "items": [
                            {
                                "type": "Container",
                                "height": "100vh",
                                "width": "100vw",
                                "paddingLeft": "@marginHorizontal",
                                "paddingRight": "@marginHorizontal",
                                "justifyContent": "center",
                                "items": [
                                    {
                                        "type": "Text",
                                        "text": "${buttonExampleData.heading}"
                                    },
                                    {
                                        "type": "Text",
                                        "text": "${buttonExampleData.subheading}"
                                    },
                                    {
                                        "type": "ButtonRow",
                                        "touchForwardSetting": False,
                                        "buttons": "${buttonExampleData.buttons}",
                                        "spacing": "@spacingMedium"
                                    }
                                ]
                            }
                        ]
                    }
                },
                "datasources": datasources
            }
        }

    if support_apl == False and (visual_type == "number_buttons" or visual_type == "boolean"):
        return {
            "should_session_end": should_session_end,
            "speak": ack + " " + audio_script,
            "reprompt": audio_script,
            "card_title": visual_property["heading"],
            "card_content": visual_property["subheading"]
        }

    if visual_type == "single_session" or visual_type == "multiple_session":
        return {
            "speak": ack + " " + audio_script,
            "reprompt": audio_script,
            "card_title": visual_property["heading"],
            "card_content": visual_property["subheading"],
            "should_session_end": should_session_end
        }

def get_time_str():
    return datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")

if __name__ == '__main__':
    # test it out
    answer = 3
    date_fetching_code = ""
    condition_code = "_answer_ > 5"
    # result = process_answer_condition(date_fetching_code, condition_code, answer)
    # print(f"result is {result}")