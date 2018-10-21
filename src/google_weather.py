def ampm_to_24(s):
    '''오후 7:00 -> 19:00, 오전 7:00 -> 7:00'''
    ss = s.split(' ')
    if ss[0] == '오후':
        return ':'.join([str(int(ss[1].split(':')[0])+12), ss[1].split(':')[1]])
    elif ss[0] == '오전':
        return ':'.join([str(int(ss[1].split(':')[0])), ss[1].split(':')[1]])
    elif ss[1] == 'PM':
        return ':'.join([str(int(ss[0].split(':')[0])+12), ss[0].split(':')[1]])
    elif ss[1] == 'AM':
        return ':'.join([str(int(ss[0].split(':')[0])), ss[0].split(':')[1]])


def reduce_day(day): return '(' + day[1] + ')'  # (일요일) -> (일)


def hhmm_to_hh(hhmm): return ('0' + hhmm[:-3])[-2:]  # 01:00, 10:00 -> 01, 10


def reduce_time(time): return (reduce_day(time.split(' ')[0]) +
                               ' ' +
                               ampm_to_24(' '.join(time.split(' ')[1:])))


import requests
from bs4 import BeautifulSoup
import json


def weather(loc=''):
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
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }
    html_text = requests.get(
        "https://www.google.co.kr/search?q={}+날씨&aqs=chrome..69i57.3675j0j1&sourceid=chrome&ie=UTF-8".format(loc), headers=headers).text

    # with open('orig-chrome.html', 'w', encoding='utf-8') as make_file:
    #     make_file.write(html_text)

    soup = BeautifulSoup(html_text, 'html.parser')

    loc = soup.find(id='wob_loc')
    # print(loc.text)
    time = soup.find(id='wob_dts')
    # print(time.text)
    cond = soup.find(id='wob_dc')
    # print(cond.text)
    tm = soup.find(id='wob_tm')
    # print(tm.text)
    pp = soup.find(id='wob_pp')
    # print(pp.text)
    hm = soup.find(id='wob_hm')
    # print(hm.text)
    ws = soup.find(id='wob_ws')
    # print(ws.text)
    script = soup.find_all('script')
    including_script_text = list(
        filter(lambda s: 'wobist' in s.text, script))[0].text
    list_of_dict_celcious = json.loads(including_script_text[
        including_script_text.find('wobhl":')+7:including_script_text.find('wobist')-2])[::1]  # changed from 2
    three_hours = list_of_dict_celcious[::3][1:9]

    ret = '\n'.join(
        ['{}  {}  {}  {}℃'.format(loc.text, reduce_time(time.text), cond.text, tm.text),
            '강수 {}  습도 {}  풍속 {}'.format(pp.text, hm.text, ws.text)]
        +
        ['{}  {}  {}℃'.format(
            hhmm_to_hh(ampm_to_24(' '.join((h['dts'].split(' ')[1:])))), h['c'], h['tm'])
         for h in three_hours]
    )
    return ret
