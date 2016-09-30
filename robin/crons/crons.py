import re
import logging
import iso8601
import pytz


from datetime import timedelta, date
from django.db import transaction as dbtransaction
from commons import common_helpers
from members.models import Member
from statistics.models import Repository, Pull, Commit, Comment
from scripts.githublight import Repository as Repo


logger = logging.getLogger(__name__)

# project's time zone, in settings.py
TIME_ZONE = common_helpers.get_config('TIME_ZONE')
# Github ACCESS_TOKEN, API rate limit 5000/H
ACCESS_TOKEN = common_helpers.get_config('ACCESS_TOKEN')


def date_generartor():
    """
    generrats query params :since , until
    """
    # UTC time
    today = iso8601.parse_date(date.today().isoformat())
    # 8 hours offset
    tz_offset = timedelta(hours=8)
    # since the very beginning of the yesterday local time(Beijing, China)
    since = today - timedelta(days=60) - tz_offset  # for debug purpose, days=60 will be changed to 1 later
    # until the last secs of the yesterday local time(Beijing, China)
    until = today - timedelta(seconds=1) - tz_offset
    return since, until


def utc2local_parser(date):
    """
    load utc date string into local(Beijing) date ojetcs.
    """
    return iso8601.parse_date(date).astimezone(pytz.timezone(TIME_ZONE))


def _test(content):
    pass


def _create_comments(comments, comment_type, pull_db, members):
    """
    creates comments of a pull.
    type 0 : comments
    type 1 : review comments
    """
    for comment in comments:
        # comments that commented by members are count.
        if comment['user']['login'] in [member.github_account for member in members]:
            Comment.objects.create(comment_id=comment['id'],
                                   author=comment['user']['login'],
                                   comment_type=comment_type,
                                   body=comment['body'],
                                   created_at=str(utc2local_parser(comment['created_at']))[:-6],
                                   updated_at=str(utc2local_parser(comment['updated_at']))[:-6],
                                   pull=pull_db
                                   )


# @dbtransaction.atomic
def auto_load_commits_of_members():
    """
    load T-1 commits of all members into database.
    """
    # !!! there is an API rate limit, https://developer.github.com/v3/#rate-limiting
    members = Member.objects.all()
    repositories = Repository.objects.all()  # from database
    since, until = date_generartor()

    for repository in repositories:
        repo = Repo(repository.owner, repository.repo)
        # print repository
        # print repository log
        for member in members:
            # print member
            commits = repo.get_commits_by_email(member.rh_email, since, until, access_token=ACCESS_TOKEN)
            for commit in commits:
                Commit.objects.create(sha=commit['sha'],
                                      author=commit['commit']['author']['name'],
                                      email=commit['commit']['author']['email'],
                                      date=str(utc2local_parser(commit['commit']['author']['date']))[:-6],
                                      message=commit['commit']['message'],
                                      repository=repository
                                      )


@dbtransaction.atomic
def auto_load_pulls():
    """
    load the latest page of pull request and its comment, commits into database.
    """
    members = Member.objects.all()
    repositories_db = Repository.objects.all()  # from database
    since, until = date_generartor()

    for repository_db in repositories_db:
        print repository_db
        repo = Repo(repository_db.owner, repository_db.repo)
        # due to can not get pulls by date, everyday get latest 30.
        pulls = repo.get_pulls(page=1, access_token=ACCESS_TOKEN)
        # print len(pulls), 'no of pulls'
        for pull in pulls:  # debug!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # only pulls that pulled by members are count.
            if pull['user']['login'] in [member.github_account for member in members]:
                # current pull request based on number.
                pull = repo.get_pull_by_number(number=pull['number'], access_token=ACCESS_TOKEN)

                if pull['state'] == 'closed':
                    pull['state'] = 0
                if pull['state'] == 'open':
                    pull['state'] = 1
                if pull['closed_at'] is not None:
                    pull['closed_at'] = str(utc2local_parser(pull['closed_at']))[:-6]

                pull_db = Pull.objects.create(pull_number=pull['number'],
                                              title=pull['title'],
                                              author=pull['user']['login'],
                                              body=pull['body'],
                                              pull_state=pull['state'],
                                              pull_merged=pull['merged'],
                                              comments=pull['comments'],
                                              review_comments=pull['review_comments'],
                                              commits=pull['commits'],
                                              additions=pull['additions'],
                                              deletions=pull['deletions'],
                                              changed_files=pull['changed_files'],
                                              created_at=str(utc2local_parser(pull['created_at']))[:-6],
                                              updated_at=str(utc2local_parser(pull['updated_at']))[:-6],
                                              closed_at=pull['closed_at'],
                                              repository=repository_db
                                              )

                if pull_db.comments > 0:
                    #  create issue's comments in db if it exists, witch is type 0
                    comments = repo.get_issue_comments(pull['number'])
                    _create_comments(comments, 0, pull_db, members)

                if pull_db.review_comments > 0:
                    # create pull's comments in db if it exists, witch is type 1
                    comments = repo.get_pull_comments(pull['number'])
                    _create_comments(comments, 1, pull_db, members)
                if pull_db.commits > 0:
                    commits = repo.get_pull_commits(pull['number'])
                    for commit in commits:
                        # commits that commitd by members are count.
                        if commit['commit']['author']['email'] in [member.rh_email for member in members]:
                            Commit.objects.create(sha=commit['sha'],
                                                  author=commit['commit']['author']['name'],
                                                  email=commit['commit']['author']['email'],
                                                  date=str(utc2local_parser(commit['commit']['author']['date']))[:-6],
                                                  message=commit['commit']['message'],
                                                  repository=repository_db,
                                                  pull=pull_db)


def _regex_bug_id(content, regex):
    regex, res = regex, None
    text = content.encode("utf-8")
    match = regex.search(text)
    if match:
        res = re.findall(r"\d+", match.groups()[0])[0]
    return res


# todo read bug id in pull body or comments type 0
def auto_retrieve_bug_id():
    """
    load bug id into pull if pull.bug_id is null, todo discuss later!!!
    """
    pulls_db = Pull.objects.filter(bug_id=None)
    regex = re.compile(r"id:(.*)", re.M | re.I)
    # first search bug_id in pull body
    for pull_db in pulls_db:
        bug_id = None
        text = pull_db.body.encode("utf-8")
        match = regex.search(text)
        if match:
            bug_id = re.findall(r"\d+", match.groups()[0])[0]

        # if not in pull body serach from comments.
        if bug_id is None:
            comments_db = Comment.objects.filter(pull=pull_db, comment_type=0, author=pull_db.author)
            for comment_db in comments_db:
                text = comment_db.body.encode("utf-8")
                match = regex.search(text)
                if match:
                    bug_id = re.findall(r"\d+", match.groups()[0])[0]
            # print bug_id
        # print bug_id, pull_db, '*' * 24
        pull_db.bug_id = bug_id
        pull_db.save()


# todo change pull state

# =================================
# auto_load_commits_of_members()
# auto_load_issues()
# auto_load_pulls()
# auto_retrieve_bug_id()
