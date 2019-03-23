import json
from bs4 import BeautifulSoup
import requests


# exports

def get_google(loc):
    KEYWORD = '공기질'  # '미세먼지'

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3'
    }
    html_text = requests.get(
        "https://www.google.co.kr/search?q={}+{}&aqs=chrome..69i57.3675j0j1&sourceid=chrome&ie=UTF-8".format(loc, KEYWORD), headers=headers).text
    soup = BeautifulSoup(html_text, 'html.parser')

    loc = soup.find('div', {'class': 'ha9jJe gsrt'}).text
    status = {
        'level': soup.find('div', {'class': 'dGcunf gsrt'}).text,
        'message': soup.find('div', {'class': 'Us3eld'}).text.split('.')[0] + '.'
    }
    major_pollutant = {
        'text': soup.find('span', {'class': 'j9f4tb'}).text,
        'type': soup.find('span', {'class': 'TFBdJd'}).text,
        'value': soup.find('div', {'class': 'uULQNc'}).text
    }
    info = {
        'index': soup.find('span', {'class': 'zN28Re'}).find_next_sibling('span').text,
        'time_message': soup.find('span', {'class': 'Q6owNe'}).find_next_sibling('span').text[:-3],
        # from 교체필요
        'from': soup.find('span', {'class': 'zN28Re'}).find_next_sibling('span').text
    }
    return {'KEYWORD': KEYWORD, 'loc': loc, 'status': status, 'major_pollutant': major_pollutant, 'info': info}


def aq(loc=''):
    '''
    Google air quality search
    '''

    texts = get_google(loc)

    res = '\n'.join([
        '{}, {}'.format(texts['loc'], texts['info']['time_message']),
        '{}: {}({})'.format(
            texts['info']['index'], texts['status']['level'], texts['major_pollutant']['value']),
        '{} {}'.format(
            texts['major_pollutant']['text'], texts['major_pollutant']['type']),
        # '',
        '{}'.format(texts['status']['message']),
        # '',
        # '{}. {}'.format(, texts['info']['from'])
    ])
    return res
