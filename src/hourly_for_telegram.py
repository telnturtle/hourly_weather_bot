import json
import os
import sys
import traceback
if True:
    sys.path.append(os.path.dirname(__file__))
    import google_aq
    import google_weather


def make_payload(chat_id, query, aq=False, daily=False):
    # the query is too long
    if len(query) > 255:
        return ['You called with a very long location.']

    # payload_list: [hourly] or
    # [hourly, air quality] or
    # [hourly, daily] or
    # [hourly, air quality, daily]
    payload_list = google_weather.hourly_daily(query, daily=daily)

    if aq:
        try:
            aq_payload = google_aq.aq(query)
            payload_list.insert(1, aq_payload)
        except Exception:
            traceback.print_exc()

    return payload_list
