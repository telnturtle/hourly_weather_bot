import sys
from datetime import datetime, time, timedelta
import queue
import os
import time
import json
import traceback

import wunderground
import transloc
import loggingmod


def condition_hourly(location):
    '''Condition + hourly, 앞으로 14시간동안 상태를 두시간 간격으로 나타낸다'''
    # 한국어 위치를 시군 단위의 영어 이름으로 바꾼다. 영어 단어면 바꾸지 않는다.
    transed_location = transloc.translate(location)

    # 위치가 한국어라면
    location_is_korean = transloc.is_korean(location)

    # 위치가 한국어이며 찾지 못하는 곳이라면
    if location_is_korean and transed_location == None:
        return '위치({})를 찾을 수 없습니다.'.format(location)

    # 날씨 json을 갱신하고 저장하고 가져온다
    condition_data = wunderground.condition(transed_location, is_korean=location_is_korean)
    hourly_data = None

    _hourly_call = 4
    while _hourly_call > 0:
        # Wunderground API가 뻗어있다면 None을 돌려받는다.
        if condition_data is None:
            return '{}, {} {}\n{} {}°C {} RH {}\n'.format('', '', '', '', '', '', '')
        
        elif type(condition_data) == dict:
            # 위치가 영어이며 찾지 못하는 곳이라면
            if 'error' in condition_data['response']:
                return 'City Not Found\n\nThe search for "{}" did not return any results.'.format(location)
        
            # 위치를 찾았으며 리스트 결과를 돌려받았다면
            elif 'results' in condition_data['response']:
                new_location = 'zmw:' + condition_data["response"]["results"][0]['zmw']
                condition_data = wunderground.condition(new_location, is_korean=False)
                hourly_data = wunderground.hourly(new_location, is_korean=False)
            
            else:
                hourly_data = wunderground.hourly(transed_location, is_korean=location_is_korean)
        
        else: 
            hourly_data = wunderground.hourly(transed_location, is_korean=location_is_korean)

        _hourly_call = _hourly_call - 1
        if hourly_data["hourly_forecast"]:  break

    del _hourly_call

    # 
    # Condition
    # 

    # Full location
    _full_loc = condition_data['current_observation']['display_location']['full']
    
    ___temp =  condition_data['current_observation']['observation_time_rfc822'].split(' ') # Three underscores
    
    # Day of the week
    try: _day_of_the_week = ___temp[0][:-1]
    except Exception as e: _day_of_the_week = ''
    
    # Day
    try: _dd = int(___temp[1])
    except Exception as e: _dd = ''
    
    conditions_m = datetime.fromtimestamp(int(condition_data['current_observation']['observation_epoch'])).month
    conditions_y = datetime.fromtimestamp(int(condition_data['current_observation']['observation_epoch'])).year
    
    # Time
    try: _time = ___temp[4][:5]
    except: _time = "error"
    
    # Weather
    _weat = condition_data['current_observation']['weather']
    
    # 바로 이전 줄에 표시한 컨디션을 저장한다
    _prev_cond = _weat
    
    # Rounded Celsius
    # _round = lambda x: int(x + 0.5) if x >= 0 else int(x - 0.5)
    def _round(x):
        x = float(x)
        return int(x + 0.5) if x >= 0 else int(x - 0.5)
    _temp_c = _round(condition_data['current_observation']['temp_c'])
    
    # Relative humidity
    _relat_hum = condition_data['current_observation']['relative_humidity']
    
    _ret = '{}, {} {}\n{} {}°C {} RH {}\n'.format(_full_loc, _day_of_the_week, _dd, _time, _temp_c, _weat, _relat_hum)
    
    # 
    # 

    # 현재 시간과 날짜
    now_hour = int(_time[:2])
    now_day = int(_dd)
    now_ymd = datetime(year=conditions_y, month=conditions_m, day=now_day)

    # 
    # Hourly가 자꾸 생략되거나 줄어드는 문제로 디버깅하려고
    # 
    _filename = str(datetime.now().strftime('%Y%m%dT%H%M%S.%f')) + 'L' + str(transed_location) + '.json'
    
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath( __file__ )), '..', '__debug', '_log', _filename), 'w', encoding='utf-8') as make_file:
            json.dump(hourly_data, make_file, ensure_ascii=False, indent='\t')
    except Exception as e:
        loggingmod.logger.warning("Error at condition_hourly({})".format(location))
        loggingmod.logger.warning(e)

    # 
    # Hourly
    # 

    # Wunderground API가 뻗어있다면 None을 돌려받는다.
    if hourly_data is None:
        loggingmod.logger.info("hourly_data is None")
        return _ret
    
    # hourly_initial_time + time_interval x (_count-1) 시간 뒤까지 예보한다
    _count = 7 # hourly는 _count개 줄로 나타냄
    time_interval = 2
    hourly_initial_time = 2
    
    # 처음으로 다음 날짜로 넘어가면 요일과 날짜를 나타낸다
    _next_day_first = True

    # _ret에 _count개 줄을 추가한다
    for hourly in hourly_data['hourly_forecast']:
        _hour = ('0'+str(int(hourly['FCTTIME']['hour'])))[-2:]  # 시간
        _mday = int(hourly['FCTTIME']['mday'])                  # 날짜
        _mon = int(hourly['FCTTIME']['mon'])
        _year = int(hourly['FCTTIME']['year'])
        _weekday = hourly['FCTTIME']['weekday_name_abbrev']     # 요일
        _epoch = int(hourly['FCTTIME']['epoch'])                # 유닉스타임 # GMT
        _cel = _round(hourly['temp']['metric'])                 # 섭씨
        _cond = hourly['condition']                             # 컨디션
        
        # time_interval 시간 간격에 맞춰 나타낸다
        if (int(_hour) - now_hour) % time_interval != hourly_initial_time % time_interval:
            loggingmod.logger.info('_hour = {}: Time interval: continue'.format(_hour))
            continue
        
        # 현재 시간보다 이전의 정보를 표시하지 않는다
        if _epoch + 100 < int(time.time()):
            loggingmod.logger.info('_hour = {}: epoch < now'.format(_hour))
            continue

        # 처음으로 다음 날짜로 넘어가면 요일과 날짜를 나타낸다
        if _next_day_first and datetime(year=_year, month=_mon, day=_mday) == now_ymd + timedelta(days=1):
            _hour = '{} {}\n{}'.format(_weekday, _mday, _hour)
            _next_day_first = False
        
        # 컨디션이 이전과 같다면 표시하지 않는다, 아니라면 앞에 공백 하나를 추가한다
        ___cond = ' '+_cond if _cond != _prev_cond else ''
        _prev_cond = _cond
        
        # 결과 텍스트에 한 줄을 추가한다
        _ret += '{} {}°C{}\n'.format(_hour, _cel, ___cond)
        
        _count -= 1
        
        # 줄 수 제한
        if _count == 0:
            break

    return _ret


def condition_forecast(location):
    '''Condition + forecast'''
    # 한국어 위치를 시군 단위의 영어 이름으로 바꾼다. 영어 단어면 바꾸지 않는다.
    transed_location = transloc.translate(location)

    # 위치가 한국어라면
    location_is_korean = transloc.is_korean(location)

    # 위치가 한국어이며 찾지 못하는 곳이라면
    if location_is_korean and transed_location == None:
        return '위치({})를 찾을 수 없습니다.'.format(location)

    # 날씨 json을 갱신하고 저장하고 가져온다
    condition_data = wunderground.condition(transed_location, is_korean=location_is_korean)

    # Wunderground API가 뻗어있다면 None을 돌려받는다.
    if condition_data is None:
        return '{}, {} {}\n{} {} C {} RH {}\n'.format('', '', '', '', '', '', '')
    
    # 위치가 영어이며 찾지 못하는 곳이라면
    elif type(condition_data) == dict:
        if 'error' in condition_data['response']:
            return 'City Not Found\n\nThe search for "{}" did not return any results.'.format(location)
    
    # 위치를 찾았으며 리스트 결과를 돌려받았다면
    elif 'results' in condition_data['response']:
        new_location = 'zmw:' + condition_data["response"]["results"][0]['zmw']
        condition_data = wunderground.condition(new_location, is_korean=False)
        forecast_data = wunderground.forecast(new_location, is_korean=False)
    
    else: forecast_data = wunderground.forecast(transed_location, is_korean=location_is_korean)

    # Condition
    
    # Full location
    _full_loc = condition_data['current_observation']['display_location']['full']
    
    ___temp =  condition_data['current_observation']['observation_time_rfc822'].split(' ') # Three underscores
    
    # Day of the week
    try: _day_of_the_week = ___temp[0][:-1]
    except Exception as e: _day_of_the_week = ''
    
    # Day
    try: _dd = int(___temp[1])
    except Exception as e: _dd = ''
    
    # Time
    try: _time = ___temp[4][:5]
    except: _time = "error"
    
    # Weather
    _weat = condition_data['current_observation']['weather']
    
    # 바로 이전 줄에 표시한 컨디션을 저장한다
    _prev_cond = _weat
    
    # Rounded Celsius
    _round = lambda x: int(x + 0.5) if x >= 0 else int(x - 0.5)
    _temp_c = _round(condition_data['current_observation']['temp_c'])
    
    # Relative humidity
    _relat_hum = condition_data['current_observation']['relative_humidity']
    
    _ret = '{}, {} {}\n{} {} C {} RH {}\n'.format(_full_loc, _day_of_the_week, _dd, _time, _temp_c, _weat, _relat_hum)

    # Forecast
    try:
        _fcttext_metric = forecast_data['forecast']['txt_forecast']['forecastday'][0]['fcttext_metric']
        _ret += _fcttext_metric
    except Exception as e:
        loggingmod.logger.warning(e)
        # TODO: try-except 없애기
    
    return _ret
