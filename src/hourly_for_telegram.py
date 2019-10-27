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
