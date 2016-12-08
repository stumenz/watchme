#!/usr/bin/python3

import requests
import logging
import re
import json

from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, HTTPError
from typing import Dict

Json = Dict[str, str]

log = logging.getLogger(__name__)


def series_details(series_url: str) -> BeautifulSoup:
    try:
        response = requests.get(series_url)
        return BeautifulSoup(response.text)
    except (ConnectionError, HTTPError):
        raise


def check_episode_numbers(episode_number: str) -> bool:
    "check if episode numbers are valid"
    if 0 < int(episode_number) <= 26:
        return True


def check_season_number(season_number: str) -> bool:
    "check if season number is valid"
    if int(season_number) > 0:
        return True


def modify_episode_number(season_value: str, episode_value: str) -> str:
    "format episode number to eg S01E02"
    if int(season_value) < 10:
        season_value = "0{}".format(season_value)
    if int(episode_value) < 10:
        episode_value = "0{}".format(episode_value)
    return''.join(('S', season_value, 'E', episode_value))


def primewire(series_url: str) -> Json:
    try:
        series_episodes = []
        series_info = {}
        series_html = series_details(series_url)
        total_seasons = len(series_html.find_all('a',
                                                 {'class': 'season-toggle'}))
        total_episodes = len(series_html.find_all('div',
                                                  {'class': 'tv_episode_item'}))
        series_info['total_seasons'] = total_seasons
        series_info['total_episodes'] = total_episodes
        for episode in series_html.find_all('div', {'class': 'tv_episode_item'}):
            link = episode.a['href']
            link_data = re.search(r'season-(\d+)-episode-(\d+)', link)
            if check_season_number(link_data.group(1)) and check_episode_numbers(link_data.group(2)):
                episode_number = modify_episode_number(link_data.group(1), link_data.group(2))
                episode_name = episode.find('a').contents[1].text
                episode_dict = {
                    'episode_link': link,
                    'episode_number': episode_number,
                    'episode_name': episode_name
                }
                series_episodes.append(episode_dict)
        series_info['episodes'] = series_episodes
        return json.dumps(series_info)
    except (ConnectionError, HTTPError) as error:
        log.error("Unable to connect to primewire")
        log.exception(error)
