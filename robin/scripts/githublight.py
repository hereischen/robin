# -*- coding: utf-8 -*-

import requests

GITHUB_API = 'https://api.github.com'


class Repository(object):

    def __init__(self, owner, repo):
        self.url = '/'.join([GITHUB_API, 'repos', owner, repo])
        self.user = "hereischen"

    def get_commits_by_email(self, email=None, since=None, until=None, page=1, access_token=None):
        url = '/'.join([self.url, 'commits'])
        params = {'since': since, 'until': until, 'author': email, 'page': page}
        r = requests.get(url, params=params, auth=(self.user, access_token))
        return r.json()

    def get_issues(self, since=None, page=1, state='all', access_token=None):
        url = '/'.join([self.url, 'issues'])
        # based on observations, default items returned by guthub api v3 is 30
        per_page = 30
        res = []
        while True:
            params = {'since': since, 'page': page, 'state': state}
            r = requests.get(url, params, auth=(self.user, access_token))
            res.extend(r.json())
            page += 1

            if len(r.json()) < per_page:
                break
        return res

    def get_pulls(self, page=0, state='all', access_token=None):
        url = '/'.join([self.url, 'pulls'])
        # based on observations, default items returned by guthub api v3 is 30
        page_depth = 0
        per_page = 30
        res = []
        if page_depth == page:
            while True:
                page += 1
                params = {'page': page, 'state': state}
                r = requests.get(url, params, auth=(self.user, access_token))
                res.extend(r.json())
                if len(r.json()) < per_page:
                    break
        else:
            while page_depth < page:
                page_depth += 1
                params = {'page': page_depth, 'state': state}
                r = requests.get(url, params, auth=(self.user, access_token))
                res.extend(r.json())
                if len(r.json()) < per_page:
                    break
        return res

    def get_a_page_of_issues(self, page=1, since=None, state='all', access_token=None):
        url = '/'.join([self.url, 'issues'])
        params = {'since': since, 'page': page, 'state': state}
        r = requests.get(url, params, auth=(self.user, access_token))
        return r.json()

    def get_issue_by_number(self, number, access_token=None):
        url = '/'.join([self.url, 'issues', str(number)])
        r = requests.get(url, auth=(self.user, access_token))
        return r.json()

    def get_issue_comments(self, number, access_token=None):
        # just comments
        url = '/'.join([self.url, 'issues', str(number), 'comments'])
        r = requests.get(url, auth=(self.user, access_token))
        return r.json()

    def get_pull_comments(self, number, access_token=None):
        # review comments
        url = '/'.join([self.url, 'pulls', str(number), 'comments'])
        r = requests.get(url, auth=(self.user, access_token))
        return r.json()

    def get_pull_by_number(self, number, access_token=None):
        url = '/'.join([self.url, 'pulls', str(number)])
        r = requests.get(url, auth=(self.user, access_token))
        return r.json()

    def get_pull_commits(self, number, access_token=None):
        url = '/'.join([self.url, 'pulls', str(number), 'commits'])
        r = requests.get(url, auth=(self.user, access_token))
        return r.json()


# *************************************************************************
# print Repository('hereischen', 'robin').get_commits_by_email(email='hachen@redhat.com', until='2016-09-16T05:50:35Z')
# print Repository('avocado-framework', 'avocado-vt').get_issues()
# print Repository('avocado-framework', 'avocado-vt').get_a_page_of_issues(page=2)
# print Repository('avocado-framework', 'avocado-vt').get_issue_by_number('709')
# print len(Repository('avocado-framework', 'avocado-vt').get_issue_comments('557'))
# print Repository('avocado-framework', 'avocado-vt').get_pull_by_number('709')
# print Repository('avocado-framework', 'avocado-vt').get_pull_commits('709')
# print Repository('avocado-framework', 'avocado-vt').get_pulls()
# print len(Repository('avocado-framework', 'avocado-vt').get_pull_comments('699'))
