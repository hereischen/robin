# -*- coding: utf-8 -*-

import requests

GITHUB_API = 'https://api.github.com'


class Repository(object):

    def __init__(self, owner, repo):
        self.url = '/'.join([GITHUB_API, 'repos', owner, repo])

    # def get_repo(self):
    #     repo = requests.get(self.url).json()
    #     return repo

    def get_commits_by_email(self, email=None, since=None, until=None, page=1, access_token=None):
        url = '/'.join([self.url, 'commits'])
        params = {'since': since, 'until': until, 'author': email, 'page': page, 'access_token': access_token}
        r = requests.get(url, params=params)
        return r.json()

    def get_issues(self, page=1, since=None, access_token=None):
        url = '/'.join([self.url, 'issues'])
        params = {'since': since, 'page': page, 'access_token': access_token}
        r = requests.get(url, params)
        return r.json()

    def get_issue_by_number(self, number, access_token=None):
        url = '/'.join([self.url, 'issues', number])
        params = {'access_token': access_token}
        r = requests.get(url, params)
        return r.json()

    def get_issue_comments(self, number, access_token=None):
        url = '/'.join([self.url, 'issues', number, 'comments'])
        params = {'access_token': access_token}
        r = requests.get(url, params)
        return r.json()

    def get_pull_by_number(self, number, access_token=None):
        url = '/'.join([self.url, 'pulls', number])
        params = {'access_token': access_token}
        r = requests.get(url, params)
        return r.json()

    def get_pull_commits(self, number, access_token=None):
        url = '/'.join([self.url, 'pulls', number, 'commits'])
        params = {'access_token': access_token}
        r = requests.get(url, params)
        return r.json()


# *************************************************************************
# print Repository('hereischen', 'robin').get_commits_by_email(email='hachen@redhat.com', until='2016-09-16T05:50:35Z')
# print Repository('avocado-framework', 'avocado-vt').get_issues()
# print Repository('avocado-framework', 'avocado-vt').get_issue_by_number('709')
# print len(Repository('avocado-framework', 'avocado-vt').get_issue_comments('557'))
# print Repository('avocado-framework', 'avocado-vt').get_pull_by_number('709')
# print Repository('avocado-framework', 'avocado-vt').get_pull_commits('709')
