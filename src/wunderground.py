import sys
import json
from datetime import datetime, time, timedelta
import requests
import queue
import time
import os
import traceback

# Init

# 쿼리 URL
url_conditions_korea       = 'http://api.wunderground.com/api/{}/conditions/q/KR/{}.json'
url_conditions_not_korea   = 'http://api.wunderground.com/api/{}/conditions/q/{}.json'
url_hourly                 = 'http://api.wunderground.com/api/{}/hourly/q/{}.json'
url_forecast               = 'http://api.wunderground.com/api/{}/forecast/q/{}.json'

# Wunderground API key
with open(os.path.join(os.path.dirname(os.path.abspath( __file__ )), '..', 'rsc', '_keys', 'keys'), 'r') as f:
    _key = f.readlines()[7][:-1]

# Key 삽입
url_conditions_korea = url_conditions_korea.format(_key, '{}')
url_conditions_not_korea = url_conditions_not_korea.format(_key, '{}')
url_hourly = url_hourly.format(_key, '{}')
url_forecast = url_forecast.format(_key, '{}')

# 위치를 키로 가지는 날씨 데이터를 저장하는 딕셔너리
data_condition = dict()
data_hourly = dict()
data_forecast = dict()

# Wunderground의 무료 플랜은 1분에 10, 24시간에 500 이하로만 콜해야 한다
# int 유닉스타임
# TODO: DB 저장
call_per_minute = queue.Queue(10)
call_per_24h = queue.Queue(500)

# Wunderground에 location으로 쿼리를 넣은 시간을 int 유닉스타임으로 저장한다
time_wun_called = dict()


def condition(location, is_korean=False):
    '''현재 위치 + 시간 + 날씨.'''
    # location: 번역된 영어
    
    # 현재 시각, int UTC+0 Unix timestamp
    time_now = int(time.time())
    
    # 같은 위치로 부른 간격이 minimum interval(초)이 되지 않았다면
    # 데이터를 새로 갱신하지 않고, 이전걸 그대로 사용한다
    minimum_interval_sec = 1*60*60

    if location in time_wun_called:
        if time_now - time_wun_called[location] < minimum_interval_sec:
            # data_condition에 location으로 
            # None이 아닌 데이터가 들어있어야 이전 데이터를 리턴할 수 있다. 
            if location in data_condition:
                if data_condition[location]:
                    return data_condition[location]

    # URL에 location 삽입
    if is_korean: url = url_conditions_korea.format(location)
    else: url = url_conditions_not_korea.format(location)
    
    # 콜 지연에 sleep() 사용

    # 1분에 10콜
    if not call_per_minute.full(): pass
    else:
        _diff = time_now - call_per_minute.get_nowait() 
        if 1*60 - 2 > _diff:
            _sleepsec = 1*60 - _diff
            print('Sleep {}s... at'.format(_sleepsec), datetime.now().isoformat(' ')[:19])

            time.sleep(_sleepsec)
            time_now = int(time.time())
    
    # 24시간에 500콜
    if not call_per_24h.full(): pass
    else:
        _diff = time_now - call_per_24h.get_nowait() 
        if 1*60*60*24 - 2 > _diff:
            _sleepsec = 1*60*60*24 - _diff
            print('Sleep {}s... at'.format(_sleepsec),
                datetime.now().isoformat(' ')[:19])
            
            # 이 시간이 너무 길어지면 큰일이나지만 아직 24시간에 
            # 500콜이나 들어온 적이 없으므로 그냥 냅둠
            time.sleep(1*60*60*24 - _diff)
            time_now = int(time.time())

    # 큐와 DB와 딕셔너리에 현재 시간을 저장
    call_per_minute.put_nowait(time_now)
    call_per_24h.put_nowait(time_now)
    
    time_wun_called[location] = time_now
    
    # 리퀘스트 넣고 데이터를 json으로 로드한다
    response = requests.get(url=url)
    try: data = json.loads(response.text)
    except: return None
    
    # data_condition 딕셔너리에 저장한다
    data_condition[location] = data
    
    return data


def hourly(location, is_korean=False):
    '''1시간 간격으로 날씨'''
    # location: 번역된 영어
    # 현재 시각, int UTC+0 Unix timestamp
    time_now = int(time.time())

    # 같은 위치로 부른 간격이 minimum interval(초)이 되지 않았다면
    # 데이터를 새로 갱신하지 않고, 이전걸 그대로 사용한다
    minimum_interval_sec = 1*60*60
    
    if location in time_wun_called:
        if time_now - time_wun_called[location] < minimum_interval_sec:
            # data_hourly에 location으로 
            # None이 아닌 데이터가 들어있어야 이전 데이터를 리턴할 수 있다. 
            if location in data_hourly:
                if data_hourly[location]:
                    return data_hourly[location]

    # URL에 location 삽입
    url = url_hourly.format(location)
    
    # 콜 지연에 sleep() 사용

    # 1분에 10콜
    if not call_per_minute.full(): pass
    else:
        _diff = time_now - call_per_minute.get_nowait() 
        if 1*60 - 2 > _diff:
            _sleepsec = 1*60 - _diff
            print('Sleep {}s... at'.format(_sleepsec), datetime.now().isoformat(' ')[:19])

            time.sleep(_sleepsec)
            time_now = int(time.time())
    
    # 24시간에 500콜
    if not call_per_24h.full(): pass
    else:
        _diff = time_now - call_per_24h.get_nowait() 
        if 1*60*60*24 - 2 > _diff:
            _sleepsec = 1*60*60*24 - _diff
            print('Sleep {}s... at'.format(_sleepsec),
                datetime.now().isoformat(' ')[:19])
            
            # 이 시간이 너무 길어지면 큰일이나지만 아직 24시간에 
            # 500콜이나 들어온 적이 없으므로 그냥 냅둠
            time.sleep(1*60*60*24 - _diff)
            time_now = int(time.time())

    # 큐와 DB와 딕셔너리에 현재 시간을 저장
    call_per_minute.put_nowait(time_now)
    call_per_24h.put_nowait(time_now)
    
    time_wun_called[location] = time_now

    # 리퀘스트 넣고 데이터를 json으로 로드한다
    response = requests.get(url=url)
    try: data = json.loads(response.text)
    except Exception as e:
        print(e) # 디버깅좀
        return None
    
    # data_hourly 딕셔너리에 저장한다
    data_hourly[location] = data
    
    return data


def forecast(self, location):
    '''오늘 예보 영어 문장'''
    # location: 번역된 영어
    
    # 현재 시각, int UTC+0 Unix timestamp
    time_now = int(time.time())

    # 같은 위치로 부른 간격이 minimum interval(초)이 되지 않았다면
    # 데이터를 새로 갱신하지 않고, 이전걸 그대로 사용한다
    minimum_interval_sec = 1*60*60
    
    if location in time_wun_called:
        if time_now - time_wun_called[location] < minimum_interval_sec:
            # data_forecast에 location으로 
            # None이 아닌 데이터가 들어있어야 이전 데이터를 리턴할 수 있다. 
            if location in data_forecast:
                if data_forecast[location]:
                    return data_forecast[location]

    # URL에 location 삽입
    url = url_forecast.format(location)
    
    # 콜 지연에 sleep() 사용

    # 1분에 10콜
    if not call_per_minute.full(): pass
    else:
        _diff = time_now - call_per_minute.get_nowait() 
        if 1*60 - 2 > _diff:
            _sleepsec = 1*60 - _diff
            print('Sleep {}s... at'.format(_sleepsec), datetime.now().isoformat(' ')[:19])

            time.sleep(_sleepsec)
            time_now = int(time.time())
    
    # 24시간에 500콜
    if not call_per_24h.full(): pass
    else:
        _diff = time_now - call_per_24h.get_nowait() 
        if 1*60*60*24 - 2 > _diff:
            _sleepsec = 1*60*60*24 - _diff
            print('Sleep {}s... at'.format(_sleepsec),
                datetime.now().isoformat(' ')[:19])
            
            # 이 시간이 너무 길어지면 큰일이나지만 아직 24시간에 
            # 500콜이나 들어온 적이 없으므로 그냥 냅둠
            time.sleep(1*60*60*24 - _diff)
            time_now = int(time.time())

    # 큐와 DB와 딕셔너리에 현재 시간을 저장
    call_per_minute.put_nowait(time_now)
    call_per_24h.put_nowait(time_now)
    
    time_wun_called[location] = time_now
    
    # 리퀘스트 넣고 데이터를 json으로 로드한다
    response = requests.get(url=url)
    try: data = json.loads(response.text)
    except: return None
    
    # data_forecast 딕셔너리에 저장한다
    data_forecast[location] = data
    
    return data
