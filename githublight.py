# -*- coding: utf-8 -*-

import time
import json
import requests
import iso8601

from datetime import datetime, timedelta

GITHUB_API = 'https://api.github.com'


def time_converter(date_str, utc2loacl=True):
    jet_lag = timedelta(hours=8)
    if utc2loacl is True:
        # adding jet_lag,from github utc to local
        date = iso8601.parse_date(date_str) + jet_lag
    else:
        date = iso8601.parse_date(date_str) - jet_lag
    return date


def repo(owner, repo):
    url = '/'.join([GITHUB_API, 'repos', owner, repo])
    print url
    r = requests.get(url)
    print r.content


def get_issue(owner, repo):
    url = '/'.join([GITHUB_API, 'repos', owner, repo,'issues'])

def get_commits(owner, repo, email=None, since=None, until=None):
    url = '/'.join([GITHUB_API, 'repos', owner, repo, 'commits'])
    params = {'since': since, 'until': until, 'author': email}
    r = requests.get(url, params=params)
    print r.json()


# repo('avocado-framework', 'avocado-vt')
# get_commits('avocado-framework', 'avocado-vt')
# '2016-09-18T08:50:35Z'
# get_commits('hereischen', 'robin', 'hachen@redhat.com',
#             until='2016-09-19T05:50:35Z')

