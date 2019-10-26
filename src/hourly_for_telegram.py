import os
import sys
import json
import traceback
if True:
    sys.path.append(os.path.dirname(__file__))
    import google_weather
    import google_aq
    # import loggingmod
    # import nalssi


PREV_LOCS = dict()  # { chat_id: previous_location }
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rsc', '_jsons', 'PREV_LOCS.json'), encoding='utf-8') as data_file:
        PREV_LOCS = dict(json.load(data_file))
except Exception as e:
    # loggingmod.logger.warning(e)
    traceback.print_exc()


def make_payload(chat_id, text, aq=False, daily=False):
    location = None

    # . means previous location
    use_prev_loc = text == '.'

    # use previous location; default is seoul
    if use_prev_loc:
        location = previous_location(chat_id)

    # too long location called
    elif len(text) > 255:
        return ['You called with a very long location.']

    # normal case
    else:
        location = text

    # payload_list: [hourly] or [h,, air quality] or [h., daily] or [h., aq., d.]
    payload_list = google_weather.hourly_daily(location, daily=daily)
    print('payload_list')
    print(payload_list)
    if aq:
        payload_list.insert(1, google_aq.aq(location))

    # if no exception raised and previous location isn't used then
    if not use_prev_loc:
        update(chat_id, text)

    return payload_list


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
