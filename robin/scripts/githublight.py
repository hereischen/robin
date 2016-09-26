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

    def get_issues(self, since=None, page=1, state='all', access_token=None):
        url = '/'.join([self.url, 'issues'])
        # based on observations, default items returned by guthub api v3 is 30
        per_page = 30
        res = []
        while True:
            # print 'page number >>>', page
            params = {'since': since, 'page': page, 'state': state, 'access_token': access_token}
            r = requests.get(url, params)
            res.extend(r.json())
            page += 1
            # print 'len of this page', len(r.json())
            if len(r.json()) < per_page:
                break
        # print len(res)
        return res

    def get_a_page_of_issues(self, page=1, since=None, state='all', access_token=None):
        url = '/'.join([self.url, 'issues'])
        params = {'since': since, 'page': page, 'state': state, 'access_token': access_token}
        r = requests.get(url, params)
        return r.json()

    def get_issue_by_number(self, number, access_token=None):
        url = '/'.join([self.url, 'issues', str(number)])
        params = {'access_token': access_token}
        r = requests.get(url, params)
        return r.json()

    def get_issue_comments(self, number, access_token=None):
        url = '/'.join([self.url, 'issues', str(number), 'comments'])
        params = {'access_token': access_token}
        r = requests.get(url, params)
        return r.json()

    def get_pull_by_number(self, number, access_token=None):
        url = '/'.join([self.url, 'pulls', str(number)])
        params = {'access_token': access_token}
        r = requests.get(url, params)
        return r.json()

    def get_pull_commits(self, number, access_token=None):
        url = '/'.join([self.url, 'pulls', str(number), 'commits'])
        params = {'access_token': access_token}
        r = requests.get(url, params)
        return r.json()


# *************************************************************************
# print Repository('hereischen', 'robin').get_commits_by_email(email='hachen@redhat.com', until='2016-09-16T05:50:35Z')
# print Repository('avocado-framework', 'avocado-vt').get_issues()
# print Repository('avocado-framework', 'avocado-vt').get_a_page_of_issues(page=2)
# print Repository('avocado-framework', 'avocado-vt').get_issue_by_number('709')
# print len(Repository('avocado-framework', 'avocado-vt').get_issue_comments('557'))
# print Repository('avocado-framework', 'avocado-vt').get_pull_by_number('709')
# print Repository('avocado-framework', 'avocado-vt').get_pull_commits('709')
