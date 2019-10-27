import datetime
import json
from telepot.loop import MessageLoop
import os
import sys
import telepot
import time
from datetime import timedelta
import traceback

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from src import hourly_for_telegram

# telegram prev called location by each user

PREV_LOCS = dict()  # { chat_id: previous_location }
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'rsc', '_jsons', 'PREV_LOCS.json'),
              encoding='utf-8') as data_file:
        PREV_LOCS = dict(json.load(data_file))
except Exception as e:
    # loggingmod.logger.warning(e)
    traceback.print_exc()

# telegram functons


def update(chat_id, location):
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
except Exception as e:
    # loggingmod.logger.warning(
    #     "Error at update({}, {})".format(chat_id, location))
    # loggingmod.logger.warning(e)
    traceback.print_exc()


def previous_location(chat_id):
    if chat_id in PREV_LOCS:
        return PREV_LOCS[chat_id]
    else:
        update(chat_id, 'Seoul')
        return PREV_LOCS[chat_id]


# message functions


def start_msg():
    return '''
지역별 날씨를 예보합니다. 지역을 입력해주세요.
마침표 하나만 입력해서 이전 지역을 다시 사용할 수 있습니다.

/help 로 도움말을 볼 수 있습니다.
Bot command list:
/start
/help
/command
/about
'''


def help_msg():
    return '''
지역별 날씨를 예보합니다. 지역을 입력해주세요.
마침표 하나만 입력해서 이전 지역을 다시 사용할 수 있습니다.

Bot command list:
/start
/help
/command
/about
'''


def about_msg():
    return '''
Hourly Weather Bot

@telnturtle || telnturtle@gmail.com
'''


def send(bot, chat_id, msg):
    bot.sendMessage(chat_id, msg)
    now = datetime.datetime.now()
    print('chat_id: %s\nGMT    : %s\nKST    : %s\npayload: %s\n' %
          (chat_id, now.isoformat(' ')[:19],
           (now + timedelta(hours=9)).isoformat(' ')[:19], msg))
    # print('chat_id: %s\nGMT    : %s\nKST    : %s\npayload: %s\n' % (
    #     chat_id, now.isoformat(' ')[:19], (now + timedelta(hours=9)).isoformat(' ')[:19], msg))
    # print('chat_id: %s\nGMT    : %s\nKST    : %s\npayload: %s\n'
    #       % (chat_id, now.isoformat(' ')[:19],
    #          (now + timedelta(hours=9)).isoformat(' ')[:19],
    #          msg))


def main():
    def handle(msg):
        content_type, chat_type, chat_id, msg_date, _ = telepot.glance(
            msg, long=True)
        text = msg['text']

        # conditions
        is_text = content_type == 'text'
        is_command = msg['text'].startswith('/')
        is_timeover = time.time() - msg_date > 60  # unit: second

        if is_text and is_command:
            if text == '/start':
                send(bot, chat_id, start_msg())
            elif text == '/help':
                send(bot, chat_id, help_msg())
            elif text == '/about':
                send(bot, chat_id, about_msg())

        if is_text and not is_timeover and not is_command:

            # 'Sorry, an error occurred. Please try again later.'
            NO_RESULT_MSG = '일치하는 검색결과가 없습니다.'
            payload_list = []

            try:
                payload_list = hourly_for_telegram.make_payload(chat_id,
                                                                text,
                                                                aq=True,
                                                                daily=True)
            except Exception as e:
                payload_list.insert(0, NO_RESULT_MSG)
                traceback.print_exc()

            send(bot, chat_id, payload_list[0])
            for msg in payload_list[
                    1:] if payload_list[0] != NO_RESULT_MSG else []:
                send(bot, chat_id, msg)

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
