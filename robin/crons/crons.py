
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
    since = today - timedelta(days=60) - tz_offset  # for debug purpose, days=60 will be changed to 1 later
    # until the last secs of the yesterday local time(Beijing, China)
    until = today - timedelta(seconds=1) - tz_offset
    return since, until


def utc2local_parser(date):
    """
    load utc date string into local(Beijing) date ojetcs.
    """
    return iso8601.parse_date(date).astimezone(pytz.timezone(TIME_ZONE))


def _create_comments(repo, issue, issue_db, members):
    """
    creates comments of a issue.
    """
    comments = repo.get_issue_comments(issue['number'])
    for comment in comments:
        # comments that commented by members are count.
        if comment['user']['login'] in [member.github_account for member in members]:
            Comment.objects.create(comment_id=comment['id'],
                                   author=comment['user']['login'],
                                   body=comment['body'],
                                   created_at=str(utc2local_parser(comment['created_at']))[:-6],
                                   updated_at=str(utc2local_parser(issue['updated_at']))[:-6],
                                   issue=issue_db
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
def auto_load_issues():
    members = Member.objects.all()
    repositories_db = Repository.objects.all()  # from database
    since, until = date_generartor()

    for repository_db in repositories_db:
        print repository_db
        repo = Repo(repository_db.owner, repository_db.repo)
        issues = repo.get_issues(since=since, access_token=ACCESS_TOKEN)
        print len(issues), 'no of issues'
        for issue in issues[:3]:  # debug!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # issues that issued by members are count.
            if issue['user']['login'] in [member.github_account for member in members]:

                if issue['state'] == 'closed':
                    issue['state'] = 0
                if issue['state'] == 'open':
                    issue['state'] = 1
                if issue['closed_at'] is not None:
                    issue['cloesed_at'] = str(utc2local_parser(issue['cloesed_at']))[:-6]

                if 'pull_request' in issue.keys():
                    # current issue has pull request.
                    pull = repo.get_pull_by_number(number=issue['number'], access_token=ACCESS_TOKEN)
                    if pull['state'] == 'closed':
                        pull['state'] = 0
                    if pull['state'] == 'open':
                        pull['state'] = 1
                    issue_db = Issue.objects.create(issue_number=issue['number'],
                                                    title=issue['title'],
                                                    issue_by=issue['user']['login'],
                                                    issue_state=issue['state'],
                                                    body=issue['body'],
                                                    pull_state=pull['state'],
                                                    pull_merged=pull['merged'],
                                                    comments=issue['comments'],
                                                    commits=pull['commits'],
                                                    additions=pull['additions'],
                                                    deletions=pull['deletions'],
                                                    changed_files=pull['changed_files'],
                                                    created_at=str(utc2local_parser(issue['created_at']))[:-6],
                                                    updated_at=str(utc2local_parser(issue['updated_at']))[:-6],
                                                    closed_at=issue['closed_at'],
                                                    repository=repository_db
                                                    )

                    if issue_db.comments > 0:
                        #  create issue's comments in db if it exists
                        _create_comments(repo, issue, issue_db, members)

                    #  create issue's commits in db if it exists
                    commits = repo.get_pull_commits(issue['number'])
                    for commit in commits:
                        # commits that commitd by members are count.
                        if commit['commit']['author']['email'] in [member.rh_email for member in members]:
                            Commit.objects.create(sha=commit['sha'],
                                                  author=commit['commit']['author']['name'],
                                                  email=commit['commit']['author']['email'],
                                                  date=str(utc2local_parser(commit['commit']['author']['date']))[:-6],
                                                  message=commit['commit']['message'],
                                                  repository=repository_db,
                                                  issue=issue_db)

                else:
                    # in this case, current issue does not have pull requests, so it does not have commits.
                    # but it may have comments.
                    issue_db = Issue.objects.create(issue_number=issue['number'],
                                                    title=issue['title'],
                                                    issue_by=issue['user']['login'],
                                                    issue_state=issue['state'],
                                                    pull_state=9,
                                                    body=issue['body'],
                                                    comments=issue['comments'],
                                                    created_at=str(utc2local_parser(issue['created_at']))[:-6],
                                                    updated_at=str(utc2local_parser(issue['updated_at']))[:-6],
                                                    closed_at=issue['closed_at'],
                                                    repository=repository_db,
                                                    )
                    if issue_db.comments > 0:
                        #  create issue's comments in db if it exists
                        _create_comments(repo, issue, issue_db, members)


# =================================
# auto_load_commits_of_members()
# auto_load_issues()
