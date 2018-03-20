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


    def handle(msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        time_diff = time.time() - msg['date']
        time_diff_limit = 60
        text = msg['text']

        if content_type == 'text' and time_diff_limit > time_diff and not text.startswith('/'):
            payload = hourly_for_telegram.make_payload(chat_id, text)
            
            bot.sendMessage(chat_id, payload)
            print('\n')
            print('chat_id: %s\nGMT    : %s\nKST    : %s\npayload: %s\n' % (
                chat_id, 
                datetime.datetime.now().isoformat(' ')[:19],
                (datetime.datetime.now() + timedelta(hours=9)).isoformat(' ')[:19], 
                payload))
            print('\n')
    

    with open(os.path.join(os.path.dirname(os.path.abspath( __file__ )), '..', 'rsc', '_keys', 'keys'), 'r') as f:
        TOKEN = f.readlines()[9][:-1]
    
    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, handle).run_as_thread()
    print('Listening ...')

    # Keep the program running.
    while 1:
        time.sleep(10)
