import google_aq
import google_weather


def get_google(loc):
    weather = google_weather.get_google(loc)
    aq = google_aq.aq(loc)
    return {'weather': weather, 'aq': aq}


def weather_aq(loc='', period=3, nol=8):
    texts = get_google(loc)
    texts['weather']['cond']    ['뇌우', '비']
    lambda x: s.
    
    all([])
