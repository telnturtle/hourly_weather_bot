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

    import loggingmod

    def start_msg():
        return '''
Weatherbot forecasts hourly weather.
/help to see help message.

매 시간 날씨를 예보하는 봇입니다.
/help 를 입력하여 도움말을 볼 수 있습니다.
'''

    def help_msg():
        return '''
You can enter the location to see the forecast. e.g
  san francisco ca
  tokyo japan
  london uk
  hongkong

You can use the previous location by entering a period. e.g.
  .

위치로 지역 이름을 입력하면 해당 예보를 출력합니다.
예) 서울
    판암역
    인천 논현동
    경북대
    첨단동

마침표 하나를 입력해 이전과 똑같은 위치를 사용할 수 있습니다.
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
        loggingmod.logger.info('chat_id: %s\nGMT    : %s\nKST    : %s\npayload: %s\n' % (
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
                payload = hourly_for_telegram.make_payload(chat_id, text)
                payload = (payload.replace('Rain', 'Rain☔')
                           .replace('Thunderstorm', 'Thunderstorm⛈')
                           .replace('Cloudy', 'Cloudy☁️')
                           .replace('Clouds', 'Clouds☁️')
                           .replace('Clear', 'Clear☀️')
                           .replace('Overcast', 'Overcast☁️'))
            except Exception as e:
                payload = 'Sorry, an error occurred. Please try again later.'
                loggingmod.logger.error(e, exc_info=True)
            send_msg(bot, chat_id, payload)

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rsc', '_keys', 'keys'), 'r') as f:
        TOKEN = f.readlines()[9][:-1]

    bot = telepot.Bot(TOKEN)
    _count = 5
    while 1:
        try:
            MessageLoop(bot, handle).run_as_thread(allowed_updates='message')
            loggingmod.logger.info('Listening ...')
            while 1:
                time.sleep(5)
        except Exception as e:
            loggingmod.logger.error(e, exc_info=True)

        _count = _count - 1
        if _count < 1:
            break

    # Keep the program running.
    while 1:
        time.sleep(10)
