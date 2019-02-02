import sys
import json
import requests
from datetime import datetime, time, timedelta, timezone
from collections import OrderedDict
import queue
import time
import os
import traceback

# import loggingmod


# Init

# Vworld API key
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rsc', '_keys', 'keys'), 'r') as f:
    vworld_key = f.readlines()[5][:-1]

# 딕셔너리 원소로, querynotfound를 반환하지 않는 한국어 시/군: querynotfound를 반환하지 않는 영어 이름 을 가지며, json 파일과 대응한다
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rsc', '_jsons', 'lookup_table.json'), 'r', encoding='utf-8') as data_file:
    LOOKUP_TABLE = json.load(data_file)
# 딕셔너리 원소로 querynotfound를 반환하는 한국어 시/군: querynotfound를 반환하지 않는 이웃동네 한국어 시/군 이름 을 가지며, json 파일과 대응한다
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rsc', '_jsons', 'redirects.json'), 'r', encoding='utf-8') as data_file:
    REDIRECTS = json.load(data_file)


def is_korean(word):
    '''완전한 한글이 한 글자 이상 있으면 True를 반환한다.'''
    if not len(word):
        return False
    # UNICODE RANGE OF KOREAN: 0xAC00 ~ 0xD7A3
    for c in word:
        if u"\uac00" < c < u"\ud7a3":
            return True
    return False


def translate(location):
    '''Wonderground 에서 querynotfound가 아닌 대답을 받는거로'''
    if not is_korean(location):
        return location
    elif location in LOOKUP_TABLE:
        return LOOKUP_TABLE[location]
    else:
        _si_gun = si_gun(location)
        if _si_gun:
            if _si_gun in LOOKUP_TABLE:
                return LOOKUP_TABLE[_si_gun]
            elif _si_gun in REDIRECTS:
                if REDIRECTS[_si_gun] in LOOKUP_TABLE:
                    return LOOKUP_TABLE[REDIRECTS[_si_gun]]
                else:
                    return None
            else:
                return None
        else:
            return None


def si_gun(location):
    '''대한민국 주소의 특별시/광역시/시/군 이름을 반환함 e.g. 삼성동 -> 서울, 수원 장안동 -> 수원'''
    # For vworld.kr
    params = [
        "service=address",
        # "version=2.0",
        "request=getcoord",
        "key={}".format(vworld_key),
        "format=json",
        "errorformat=json",
        "type=road",
        "address={}".format(location),
        # "refine=true",
        "simple=false",
        # "crs=epsg:4326"
    ]

    _str = "http://api.vworld.kr/req/address?{}".format("&".join(params))
    _result = requests.get(_str).json()

    try:
        if _result["response"]["status"] == "NOT_FOUND":
            return None
        else:
            _s = _result["response"]["refined"]["structure"]

            # 경기광주 따로 처리
            if _s['level1'] == '경기도' and _s['level2'] == '광주시':
                result = '경기광주'
            elif _s["level1"][-1] == "도":
                _temp = list(_s["level2"].split()[0])
                result = "".join(
                    list(filter((lambda c: c != "시" and c != "군"), _temp)))
            else:  # level1이 "시"로 끝나면
                result = _s["level1"][:2]  # level1 -> "서울특별시", "대전광역시"
            return result
    except Exception as e:
        # loggingmod.logger.warning("Error at si_gun({})".format(location))
        print("Error at si_gun({})".format(location))
        return None
