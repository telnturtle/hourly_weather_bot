import os
import sys
import json
import traceback
if True:
    sys.path.append(os.path.dirname(__file__))
    import google_weather
    # import loggingmod
    # import nalssi


PREV_LOCS = dict()  # { chat_id: previous_location }
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rsc', '_jsons', 'PREV_LOCS.json'), encoding='utf-8') as data_file:
        PREV_LOCS = dict(json.load(data_file))
except Exception as e:
    # loggingmod.logger.warning(e)
    traceback.print_exc()


def make_payload(chat_id, text):
    if text == '.':
        payload = google_weather.weather(previous_location(chat_id))
        # payload = nalssi.condition_hourly(previous_location(chat_id))
    elif len(text) > 255:
        payload = 'You called with a very long location.'

    else:
        payload = google_weather.weather(text)
        # payload = nalssi.condition_hourly(text)

        if not (payload.startswith('위치(') or payload.startswith('City Not Found')):
            update(chat_id, text)

    return payload


def update(chat_id, location):
    PREV_LOCS[chat_id] = location
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rsc', '_jsons', 'PREV_LOCS.json'), 'w', encoding='utf-8') as make_file:
            json.dump(list(PREV_LOCS.items()), make_file,
                      ensure_ascii=False, indent='\t')
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
