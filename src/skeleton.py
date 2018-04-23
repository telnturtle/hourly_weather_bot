def main():
    
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

    import datetime
    from datetime import timedelta
    
    import time
    import telepot
    from telepot.loop import MessageLoop

    from src import hourly_for_telegram

    import loggingmod


    def handle(msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        time_diff = time.time() - msg['date']
        time_diff_limit = 60
        text = msg['text']

        if content_type == 'text' and time_diff_limit > time_diff and not text.startswith('/'):
            try:
                payload = hourly_for_telegram.make_payload(chat_id, text)
            except Exception as e:
                payload = 'Sorry, an error occurred. Please try again later.'
                loggingmod.logger.error(e, exc_info=True)
            
            bot.sendMessage(chat_id, payload)
            loggingmod.logger.info('chat_id: %s\nGMT    : %s\nKST    : %s\npayload: %s\n' % (
                chat_id, 
                datetime.datetime.now().isoformat(' ')[:19],
                (datetime.datetime.now() + timedelta(hours=9)).isoformat(' ')[:19], 
                payload))
    

    with open(os.path.join(os.path.dirname(os.path.abspath( __file__ )), '..', 'rsc', '_keys', 'keys'), 'r') as f:
        TOKEN = f.readlines()[9][:-1]
    
    bot = telepot.Bot(TOKEN)
    _count = 5
    while 1:
        try:
            MessageLoop(bot, handle).run_as_thread()
            loggingmod.logger.info('Listening ...')
            while 1:
                time.sleep(5)
        except Exception as e:
            loggingmod.logger.error(e, exc_info=True)

        _count = _count - 1
        if _count < 1: break
        

    # Keep the program running.
    while 1:
        time.sleep(10)
