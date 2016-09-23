
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
    # untill the last secs of the yesterday local time(Beijing, China)
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
    members = Member.objects.all()[1:]
    repositories = Repository.objects.all()[:1]  # from database
    since, until = date_generartor()

    for repository in repositories:
        repo = Repo(repository.owner, repository.repo)
        # print repository log
        for member in members:
            commits = repo.get_commits_by_email(member.rh_email, since, until)[1:]
            for commit in commits:
                # print commit['sha']
                # print commit['commit']['author']['name']
                # print commit['commit']['author']['email']
                # print type(commit['commit']['author']['date']), utc2local_parser(commit['commit']['author']['date'])
                # print commit['commit']['message']
                # print type(repository)
                Commit.objects.create(sha=commit['sha'],
                                      author=commit['commit']['author']['name'],
                                      email=commit['commit']['author']['email'],
                                      date=utc2local_parser(commit['commit']['author']['date']),
                                      message=commit['commit']['message'],
                                      repository=repository
                                      )

# =================================
auto_load_commits_of_members()
