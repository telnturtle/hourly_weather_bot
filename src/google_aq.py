import json
from bs4 import BeautifulSoup
import requests


# exports

def aq(loc='', period=3, nol=8):
    '''

    '''
    KEYWORD = '공기질'  # '미세먼지'

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3'
    }
    html_text = requests.get(
        "https://www.google.co.kr/search?q={}+{}&aqs=chrome..69i57.3675j0j1&sourceid=chrome&ie=UTF-8".format(loc, KEYWORD), headers=headers).text
    soup = BeautifulSoup(html_text, 'html.parser')

    loc = soup.find('div', {'class': 'ha9jJe gsrt'})
    status = {
        'level': soup.find('div', {'class': 'dGcunf gsrt'}),
        'message': soup.find('div', {'class': 'Us3eld'})
    }
    major_pollutant = {
        'text': soup.find('span', {'class': 'j9f4tb'}),
        'type': soup.find('span', {'class': 'TFBdJd'}),
        'value': soup.find('div', {'class': 'uULQNc'})
    }
    info = {
        'index': soup.find('span', {'class': 'zN28Re'}).find_next_sibling('span'),
        'time_message': soup.find('span', {'class': 'Q6owNe'}).find_next_sibling('span'),
        # from 교체필요
        'from': soup.find('span', {'class': 'zN28Re'}).find_next_sibling('span')
    }

    res = '\n'.join([
        '{} {}'.format(loc.text, KEYWORD),
        '{}({}), {}'.format(
            status['level'].text, info['index'].text, major_pollutant['value'].text),
        '{} {}'.format(
            major_pollutant['text'].text, major_pollutant['type'].text),
        '',
        '{}'.format(status['message'].text),
        '',
        '{}. {}'.format(info['time_message'].text, info['from'].text)
    ])
    return res
