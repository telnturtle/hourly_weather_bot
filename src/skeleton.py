def main():

    import os
    import sys
    sys.path.append(os.path.dirname(
        os.path.abspath(os.path.dirname(__file__))))

    import datetime
    from datetime import timedelta

    import time
    import telepot
    from telepot.loop import MessageLoop

    from src import hourly_for_telegram

    # import loggingmod
    import traceback

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

    def send_msg(bot, chat_id, msg):
        bot.sendMessage(chat_id, msg)
        # loggingmod.logger.info('chat_id: %s\nGMT    : %s\nKST    : %s\npayload: %s\n' % (
        #     chat_id,
        #     datetime.datetime.now().isoformat(' ')[:19],
        #     (datetime.datetime.now() + timedelta(hours=9)).isoformat(' ')[:19],
        #     msg))
        print('chat_id: %s\nGMT    : %s\nKST    : %s\npayload: %s\n' % (
            chat_id,
            datetime.datetime.now().isoformat(' ')[:19],
            (datetime.datetime.now() + timedelta(hours=9)).isoformat(' ')[:19],
            msg))

    def handle(msg_):
        content_type, chat_type, chat_id = telepot.glance(msg_)
        time_diff = time.time() - msg_['date']
        time_diff_limit = 60
        text = msg_['text']

        if content_type == 'text' and text.startswith('/'):
            if text == '/start':
                send_msg(bot, chat_id, start_msg())
            elif text == '/help':
                send_msg(bot, chat_id, help_msg())
            elif text == '/about':
                send_msg(bot, chat_id, about_msg())

        if content_type == 'text' and time_diff_limit > time_diff and not text.startswith('/'):

            # 'Sorry, an error occurred. Please try again later.'
            NO_RESULT_MSG = '일치하는 검색결과가 없습니다.'

            try:
                payload_list = hourly_for_telegram.make_payload(
                    chat_id, text, aq=True, daily=True)
                # for weather.com only
                # payload_list[0] = (payload_list[0].replace('Rain', 'Rain☔')
                #                    .replace('Thunderstorm', 'Thunderstorm⛈')
                #                    .replace('Cloudy', 'Cloudy☁️')
                #                    .replace('Clouds', 'Clouds☁️')
                #                    .replace('Clear', 'Clear☀️')
                #                    .replace('Overcast', 'Overcast☁️'))
            except Exception as e:
                payload_list[0] = NO_RESULT_MSG
                # loggingmod.logger.error(e, exc_info=True)
                traceback.print_exc()

            send_msg(bot, chat_id, payload_list[0])
            for msg_ in payload_list[1:] if payload_list[0] != NO_RESULT_MSG else []:
                send_msg(bot, chat_id, msg_)

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rsc', '_keys', 'keys'), 'r') as f:
        TOKEN = f.readlines()[9][:-1]

    bot = telepot.Bot(TOKEN)
    _count = 5
    while 1:
        try:
            MessageLoop(bot, handle).run_as_thread(allowed_updates='message')
            # loggingmod.logger.info('Listening ...')
            print('Listening ...')
            while 1:
                time.sleep(5)
        except Exception as e:
            # loggingmod.logger.error(e, exc_info=True)
            traceback.print_exc()

        _count = _count - 1
        if _count < 1:
            break

    # Keep the program running.
    while 1:
        time.sleep(10)
