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
    '''Condition + hourly, 8 lines of [0, 6, 9, 12, 15, 18, 21] o clock'''
    # if koeran then english si / gun else id
    transed_location = transloc.translate(location)

    is_loc_kor = transloc.is_korean(location)

    # location is korean and cannot found then
    if is_loc_kor and transed_location == None:
        return '위치({})를 찾을 수 없습니다.'.format(location)

    # get condition and hourly data
    condition_data = wunderground.condition(transed_location, is_korean=is_loc_kor)
    hourly_data = None

    _hourly_call = 4
    while _hourly_call > 0:
        # None if Wunderground API dead
        if condition_data is None:
            return '{}, {} {}\n{} {}°C {} RH {}\n'.format('', '', '', '', '', '', '')
        
        elif type(condition_data) == dict:
            # location is english and cannot found then
            if 'error' in condition_data['response']:
                return 'City Not Found\n\nThe search for "{}" did not return any results.'.format(location)
        
            # if result is list
            elif 'results' in condition_data['response']:
                new_location = 'zmw:' + condition_data["response"]["results"][0]['zmw']
                condition_data = wunderground.condition(new_location, is_korean=False)
                hourly_data = wunderground.hourly(new_location, is_korean=False)
            
            else:
                hourly_data = wunderground.hourly(transed_location, is_korean=is_loc_kor)
        
        else: 
            hourly_data = wunderground.hourly(transed_location, is_korean=is_loc_kor)

        _hourly_call = _hourly_call - 1
        if hourly_data["hourly_forecast"]:  break

    del _hourly_call

    ##### condition

    # Full location
    _full_loc = condition_data['current_observation']['display_location']['full']
    
    ___temp =  condition_data['current_observation']['observation_time_rfc822'].split(' ') # Three underscores
    
    # Day of the week
    try: _wd = ___temp[0][:-1]
    except Exception as e: _wd = ''
    
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
    
    # store previous condition
    _prev_cond = _weat
    
    # Rounded Celsius
    # _round = lambda x: int(x + 0.5) if x >= 0 else int(x - 0.5)
    def _round(x):
        x = float(x)
        return int(x + 0.5) if x >= 0 else int(x - 0.5)
    _temp_c = _round(condition_data['current_observation']['temp_c'])
    
    # Relative humidity
    _rh = condition_data['current_observation']['relative_humidity']
    
    # _ret = '{}, {} {}\n{} {}°C {} RH {}\n'.format(_full_loc, _wd, _dd, _time, _temp_c, _weat, _rh)
    _ret = '{}, {}, {}\n{} {}°c {} RH {}\n'.format(_wd, _dd, _full_loc, _time, _temp_c, _weat, _rh)
    
    ##### for hourly
    now_hour = int(_time[:2])
    now_day = int(_dd)
    now_ymd = datetime(year=conditions_y, month=conditions_m, day=now_day)
    cdcooe = int(condition_data['current_observation']['observation_epoch'])

    ##### hourly

    # None if Wunderground API dead
    if hourly_data is None:
        loggingmod.logger.info("hourly_data is None")
        return _ret
    
    # _count lines hourly forecast
    _count = 8
    
    # first next day -> write date and weekday
    _next_day_first = True

    # add _count lines to return text
    for hourly in hourly_data['hourly_forecast']:
        _hour = ('0'+str(int(hourly['FCTTIME']['hour'])))[-2:]  # hour
        _mday = int(hourly['FCTTIME']['mday'])                  # month day
        _mon = int(hourly['FCTTIME']['mon'])
        _year = int(hourly['FCTTIME']['year'])
        _weekday = hourly['FCTTIME']['weekday_name_abbrev']     # weekday
        _epoch = int(hourly['FCTTIME']['epoch'])                # unixtime UTC+0
        _cel = _round(hourly['temp']['metric'])                 # celcious temp
        _cond = hourly['condition']                             # condition
        
        # only 0, 6, 9, ..., 21 o clock
        if not int(_hour) in [0,6,9,12,15,18,21]:
            loggingmod.logger.info('_hour = {}: Time interval: continue'.format(_hour))
            continue
        
        # forecast must be 1 hour later than cdcooe
        if _epoch < 3600 + cdcooe:
            loggingmod.logger.info('_hour = {}: epoch < now'.format(_hour))
            continue

        # first next day -> write date and weekday
        if _next_day_first and datetime(year=_year, month=_mon, day=_mday) == now_ymd + timedelta(days=1):
            _hour = '{} {}\n{}'.format(_weekday, _mday, _hour)
            _next_day_first = False

        # if condition is same as previous then don't write it else add a space before it
        ___cond = ' '+_cond if _cond != _prev_cond else ''
        _prev_cond = _cond
        
        # add to return text
        _ret += '{} {}°c{}\n'.format(_hour, _cel, ___cond)
        
        _count -= 1
        
        # line count
        if _count == 0:
            break

    return _ret


def condition_forecast(location):
    '''Condition + forecast'''
    # 한국어 위치를 시군 단위의 영어 이름으로 바꾼다. 영어 단어면 바꾸지 않는다.
    transed_location = transloc.translate(location)

    # 위치가 한국어라면
    is_loc_kor = transloc.is_korean(location)

    # 위치가 한국어이며 찾지 못하는 곳이라면
    if is_loc_kor and transed_location == None:
        return '위치({})를 찾을 수 없습니다.'.format(location)

    # 날씨 json을 갱신하고 저장하고 가져온다
    condition_data = wunderground.condition(transed_location, is_korean=is_loc_kor)

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
    
    else: forecast_data = wunderground.forecast(transed_location, is_korean=is_loc_kor)

    # Condition
    
    # Full location
    _full_loc = condition_data['current_observation']['display_location']['full']
    
    ___temp =  condition_data['current_observation']['observation_time_rfc822'].split(' ') # Three underscores
    
    # Day of the week
    try: _wd = ___temp[0][:-1]
    except Exception as e: _wd = ''
    
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
    _rh = condition_data['current_observation']['relative_humidity']
    
    _ret = '{}, {} {}\n{} {} C {} RH {}\n'.format(_full_loc, _wd, _dd, _time, _temp_c, _weat, _rh)

    # Forecast
    try:
        _fcttext_metric = forecast_data['forecast']['txt_forecast']['forecastday'][0]['fcttext_metric']
        _ret += _fcttext_metric
    except Exception as e:
        loggingmod.logger.warning(e)
        # TODO: try-except 없애기
    
    return _ret
