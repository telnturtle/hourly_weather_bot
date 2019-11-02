from src import hourly_for_telegram
import datetime
import json
from telepot.loop import MessageLoop
import os
from functools import reduce
import sys
import telepot
import time
from datetime import timedelta
import traceback

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


# telegram prev called location by each user

PREV_LOCS = dict()  # { chat_id: previous_location }
try:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                        'rsc', '_jsons', 'PREV_LOCS.json')
    with open(path, encoding='utf-8') as data_file:
        PREV_LOCS = dict(json.load(data_file))
except Exception as e:
    # loggingmod.logger.warning(e)
    traceback.print_exc()


# # telegram functons

def update_previous_location(chat_id, location):
    PREV_LOCS[chat_id] = location

    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                               'rsc', '_jsons', 'PREV_LOCS.json'),
                  'w',
                  encoding='utf-8') as make_file:
            json.dump(list(PREV_LOCS.items()),
                      make_file,
                      ensure_ascii=False,
                      indent='\t')
    except Exception:
        traceback.print_exc()


def get_previous_location(chat_id):
    if chat_id in PREV_LOCS:
        return PREV_LOCS[chat_id]
    else:
        update_previous_location(chat_id, 'Seoul')
        return PREV_LOCS[chat_id]


# # message functions

COMMAND_LIST = ['start', 'help', 'command', 'about']

START_MSG = '''
지역별 날씨를 예보합니다. 지역을 입력해주세요.
마침표 하나만 입력해서 이전 지역을 다시 사용할 수 있습니다.

/help 로 도움말을 볼 수 있습니다.
Bot command list:
''' + (reduce(lambda acc, val: '%s\n/%s' % (acc, val), COMMAND_LIST))

HELP_MSG = '''
지역별 날씨를 예보합니다. 지역을 입력해주세요.
마침표 하나만 입력해서 이전 지역을 다시 사용할 수 있습니다.

Bot command list:
''' + (reduce(lambda acc, val: '%s\n/%s' % (acc, val), COMMAND_LIST))


ABOUT_MSG = '''
Hourly Weather Bot by @telnturtle

telnturtle@gmail.com
'''


def message_by_command(command):
    if command == 'start':
        return START_MSG
    elif command == 'help':
        return HELP_MSG
    elif command == 'command':
        return (reduce(lambda acc, val: '%s\n/%s' % (acc, val), COMMAND_LIST))
    elif command == 'about':
        return ABOUT_MSG
    else:
        return None


def send(bot, chat_id, msg):
    bot.sendMessage(chat_id, msg)
    now = datetime.datetime.now()
    print('chat_id: %s\nGMT    : %s\nKST    : %s\npayload: %s\n' %
          (chat_id, now.isoformat(' ')[:19],
           (now + timedelta(hours=9)).isoformat(' ')[:19], msg))


# # aux functions

def is_previous_location(text):
    '''. means previous location'''
    return text == '.'


def is_content_text(content_type):
    return content_type == 'text'


def is_text_command(text):
    return text.startswith('/')


def is_time_over(date):
    return time.time() - date > 60  # unit: second


def main():

    def handle(payload):
        content_type, chat_type, chat_id, msg_date, _ = telepot.glance(
            payload, long=True)
        text = payload['text']

        # conditions
        is_text = is_content_text(content_type)
        is_command = is_text_command(payload['text'])
        is_timeover = is_time_over(msg_date)

        if not is_text:
            return

        if is_command:
            message = message_by_command(text[1:])
            if message:
                send(bot, chat_id, message)

        elif not is_timeover and not is_command:

            # make query
            is_previous_location_used = is_previous_location(text)
            query = (get_previous_location(chat_id)
                     if is_previous_location_used else text)

            # make payload
            # 'Sorry, an error occurred. Please try again later.'
            NO_RESULT_MSG = '일치하는 검색결과가 없습니다.'
            payload_list = []

            try:
                payload_list = hourly_for_telegram.make_payload(chat_id,
                                                                query,
                                                                aq=True,
                                                                daily=True)
            except Exception:
                payload_list = [NO_RESULT_MSG]
                traceback.print_exc()

            # send
            for payload in payload_list:
                send(bot, chat_id, payload)

            # update previous location
            if not is_previous_location_used:
                update_previous_location(chat_id, text)

    # run

    with open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                         'rsc', '_keys', 'keys'), 'r') as f:
        TOKEN = f.readlines()[9][:-1]

    bot = telepot.Bot(TOKEN)
    _count = 5
    while 1:
        try:
            MessageLoop(bot, handle).run_as_thread(allowed_updates='message')
            print('Listening ...')
            while 1:
                time.sleep(5)
        except Exception:
            traceback.print_exc()

        _count = _count - 1
        if _count < 1:
            break

    # keep the program running
    while 1:
        time.sleep(10)
