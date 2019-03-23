import json
from bs4 import BeautifulSoup
import requests


# aux functions

def ampm_to_24(s):
    '''오후 7:00 -> 19:00, 오전 7:00 -> 7:00'''
    ss = s.split(' ')
    if ss[0] == '오후':
        return ':'.join([str(int(ss[1].split(':')[0])+(12 if int(ss[1].split(':')[0]) % 12 != 0 else 0)), ss[1].split(':')[1]])
    elif ss[0] == '오전':
        return ':'.join([str(int(ss[1].split(':')[0])+(0 if int(ss[1].split(':')[0]) % 12 != 0 else -12)), ss[1].split(':')[1]])
    elif ss[1] == 'PM':
        return ':'.join([str(int(ss[0].split(':')[0])+(12 if int(ss[0].split(':')[0]) % 12 != 0 else 0)), ss[0].split(':')[1]])
    elif ss[1] == 'AM':
        return ':'.join([str(int(ss[0].split(':')[0])+(0 if int(ss[0].split(':')[0]) % 12 != 0 else -12)), ss[0].split(':')[1]])


def reduce_day(day):
    '''`'(일요일)'`` -> `'(일)'`'''
    return '(' + day[1] + ')'


def reduce_day_long(day):
    '''`'(일요일)'` -> `'일요일'`'''
    return day[1:-1]


def hhmm_to_hh(hhmm):
    """`'01:00'`, `'10:00'` -> `'01'`, `'10'`"""
    return ('0' + hhmm[:-3])[-2:]


def reduce_time(time): return (reduce_day_long(time.split(' ')[0]) +
                               ' ' +
                               ampm_to_24(' '.join(time.split(' ')[1:])))


# exports

def get_google(loc):
    '''
    > python .\google_weather.py
    Traceback (most recent call last):
    File ".\google_weather.py", line 59, in <module>
        weather('ㄱㄴㅇㅣㅏㅈㄱㄴㅇ자ㄱㅇㄴ')
    File ".\google_weather.py", line 44, in weather
        filter(lambda s: 'wobist' in s.text, script))[0].text
    IndexError: list index out of range
    '''
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3'
    }
    html_text = requests.get(
        "https://www.google.co.kr/search?q={}+날씨&aqs=chrome..69i57.3675j0j1&sourceid=chrome&ie=UTF-8".format(loc), headers=headers).text

    # with open('orig-chrome.html', 'w', encoding='utf-8') as make_file:
    #     make_file.write(html_text)

    soup = BeautifulSoup(html_text, 'html.parser')

    loc = soup.find(id='wob_loc').text
    time = soup.find(id='wob_dts').text
    cond = soup.find(id='wob_dc').text
    tm = soup.find(id='wob_tm').text
    pp = soup.find(id='wob_pp').text
    hm = soup.find(id='wob_hm').text
    ws = soup.find(id='wob_ws').text[:-3] + '㎧'
    script = soup.find_all('script')
    including_script_text = list(
        filter(lambda s: 'wobist' in s.text, script))[0].text.encode('ascii', 'backslashreplace').decode('unicode-escape')

    return {
        'loc': loc, 'time': time, 'condition': cond, 'temp': tm, 'pp': pp, 'humidity': hm, 'windspeed': ws, 'script-wrap': including_script_text
    }


def weather(loc='', period=3, nol=8):
    '''period(hour), nol: # of line'''
    texts = get_google(loc)

    list_of_dict_celcious = json.loads(texts['script-wrap'][texts['script-wrap'].find(
        'wobhl":')+7:texts['script-wrap'].find('wobist')-2])[::1]  # changed from 2
    period_hours = list_of_dict_celcious[::period][1:nol+1]

    ss = ['{}'.format(texts['loc']),
          '{} {}℃ {}'.format(reduce_time(
              texts['time']), texts['temp'], texts['condition']),
          '눈비 {} 습도 {} 바람 {}'.format(texts['pp'], texts['humidity'], texts['windspeed'])]
    _prev = ''
    for h in period_hours:
        _repeated = h['c'] == _prev
        c = '〃' if _repeated else h['c']
        _prev = _prev if _repeated else h['c']
        ss.append('{} {}℃ {}'.format(
            hhmm_to_hh(ampm_to_24(' '.join((h['dts'].split(' ')[1:])))), h['tm'], c))

    return '\n'.join(ss)
