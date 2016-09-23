
import logging
import iso8601
import pytz


from datetime import timedelta, date
from django.db import transaction as dbtransaction
from commons import common_helpers
from members.models import Member, Team
from statistics.models import Repository, Issue, Commit, Comment
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
    since = today - timedelta(days=1) - tz_offset
    # until the last secs of the yesterday local time(Beijing, China)
    until = today - timedelta(seconds=1) - tz_offset
    return since, until


def utc2local_parser(date):
    """
    load utc date string into local(Beijing) date ojetcs.
    """
    return iso8601.parse_date(date).astimezone(pytz.timezone(TIME_ZONE))


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
        print repository
        # print repository log
        for member in members:
            print member
            commits = repo.get_commits_by_email(member.rh_email, since, until, access_token=ACCESS_TOKEN)
            print commits
            for commit in commits:
                # print commit['sha']
                # print commit['commit']['author']['name']
                # print commit['commit']['author']['email']
                # print type(commit['commit']['author']['date']), utc2local_parser(commit['commit']['author']['date'])
                # print commit['commit']['message']
                # date = str(utc2local_parser(commit['commit']['author']['date']))[:-6]
                # print date, type(date)
                Commit.objects.create(sha=commit['sha'],
                                      author=commit['commit']['author']['name'],
                                      email=commit['commit']['author']['email'],
                                      date=str(utc2local_parser(commit['commit']['author']['date']))[:-6],
                                      message=commit['commit']['message'],
                                      repository=repository
                                      )

# def auto_load_issues_commments_commit():


# =================================
auto_load_commits_of_members()
