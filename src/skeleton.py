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
/help to see help message.
'''

    def help_msg():
        return '''
지역을 입력하세요.
예) 온수동
    인천논현
    경북대
    오사카

마침표 하나를 입력해 이전과 똑같은 지역을 쓸 수 있습니다.
예) .
'''

    def command_msg():
        return '''
/start
/help
/command
/about
'''

    def about_msg():
        return '''
About...
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

    def handle(msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        time_diff = time.time() - msg['date']
        time_diff_limit = 60
        text = msg['text']

        if content_type == 'text' and text.startswith('/'):
            if text == '/start':
                send_msg(bot, chat_id, start_msg())
                send_msg(bot, chat_id, help_msg())
            elif text == '/help':
                send_msg(bot, chat_id, help_msg())
            elif text == '/command':
                send_msg(bot, chat_id, command_msg())
            elif text == '/about':
                send_msg(bot, chat_id, about_msg())

        if content_type == 'text' and time_diff_limit > time_diff and not text.startswith('/'):
            try:
                [payload0, payload1] = hourly_for_telegram.make_payload(
                    chat_id, text, True)
                payload0 = (payload0.replace('Rain', 'Rain☔')
                            .replace('Thunderstorm', 'Thunderstorm⛈')
                            .replace('Cloudy', 'Cloudy☁️')
                            .replace('Clouds', 'Clouds☁️')
                            .replace('Clear', 'Clear☀️')
                            .replace('Overcast', 'Overcast☁️'))
            except Exception as e:
                payload0 = '일치하는 검색결과가 없습니다.'
                # payload = 'Sorry, an error occurred. Please try again later.'
                # loggingmod.logger.error(e, exc_info=True)
                traceback.print_exc()
            send_msg(bot, chat_id, payload0)
            send_msg(bot, chat_id, payload1)

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
