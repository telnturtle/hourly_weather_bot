import json
from bs4 import BeautifulSoup
import requests
import google_aq


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


def ampmhhmm_to_ampmhhsi(ampmhhmm):
    """`'오전 01:00'`, `'오전 10:00'` -> `'오전 1'`, `'오전 1'`"""
    return '%s%s' % (ampmhhmm[:-3], '시')


def reduce_time(time):
    return (reduce_day(time.split(' ')[0]) +
            ' ' +
            ' '.join(time.split(' ')[1:]))


def aux_weekday_to_dict(soup_object):
    weekday = soup_object.find(class_='vk_lgy').text

    div_list = soup_object.find_all('div')
    weather = div_list[1].find('img')['alt']
    # high_temp = div_list[2].find(class_='vk_gy')
    # print('high_temp')
    # print(high_temp)
    high = div_list[2].find(class_='vk_gy').find_all('span')[0].text
    low = div_list[2].find(class_='vk_lgy').find_all('span')[0].text

    return {'weekday': weekday, 'weather': weather, 'high': high, 'low': low}


def velocity_to_kph(vel):
    '''xm/s or xkm/h -> x㎧'''
    if vel.endswith('km/h'):
        return '%s%s' % (vel[:-4], 'kph')
    else:
        return str(round(float(vel[:-3]) / 10 * 37)) + 'kph'
    # kph or ㎧


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
    # AB test ('3㎧')
    # A
    # ws = soup.find(id='wob_ws').text[:-3] + '㎧'
    # B
    ws = velocity_to_kph(soup.find(id='wob_ws').text)
    # /AB test
    script = soup.find_all('script')
    including_script_text = list(
        filter(lambda s: 'wobist' in s.text, script))[0].text.encode('ascii', 'backslashreplace').decode('unicode-escape')

    week = list(map(aux_weekday_to_dict, soup.find(
        id="wob_dp").find_all(class_="wob_df")))

    return {
        'loc': loc, 'time': time, 'condition': cond, 'temp': tm, 'pp': pp, 'humidity': hm, 'windspeed': ws, 'script-wrap': including_script_text, 'week': week
    }


def hourly_daily(loc='', period=3, nol=8, daily=False):
    google_result = get_google(loc)

    ret = [hourly(google_result, period, nol)]

    if daily:
        ret.append(daily_(google_result['week']))
    return ret


def aux_daily(week):
    '''weekday, weather, high, low'''
    # python 버전이 다르니까 dictionary 순서가 사전순정렬 / 입력순서 두개로 나뉘어진다 ㅠ
    return '{}: {}ㆍ{}–{}℃'.format(week['weekday'], week['weather'], week['high'], week['low'])


def daily_(week):
    return '\n'.join(map(aux_daily, week))


def hourly(texts, period, nol):
    '''hourly. period(hour), nol: # of line'''
    list_of_dict_celcious = json.loads(texts['script-wrap'][texts['script-wrap'].find(
        'wobhl":')+7:texts['script-wrap'].find('wobist')-2])[::1]  # changed from 2
    period_hours = list_of_dict_celcious[::period][1:nol+1]

    ss = ['{}ㆍ{}'.format(reduce_time(texts['time']), texts['loc']),
          ('{}ㆍ{}℃ㆍ풍속 {}ㆍ강수확률 {}ㆍ습도 {}'
           .format(texts['condition'],
                   texts['temp'], texts['windspeed'], texts['pp'], texts['humidity']))
          ]
    _prev = ''
    for h in period_hours:
        _repeated = h['c'] == _prev
        c = '〃' if _repeated else h['c']
        _prev = _prev if _repeated else h['c']
        ss.append('{}: {}ㆍ{}℃'.format(
            ampmhhmm_to_ampmhhsi(' '.join((h['dts'].split(' ')[1:]))), c, h['tm']))

    return '\n'.join(ss)
