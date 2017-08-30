import re
import logging
import iso8601
import pytz


from datetime import timedelta, date, datetime
from django.db import transaction as dbtransaction
from commons import common_helpers
from members.models import Member
from statistics.models import Repository, Pull, Comment
from scripts.githublight import Repository as Repo


logger = logging.getLogger(__name__)

# project's time zone, in settings.py
TIME_ZONE = common_helpers.get_config('TIME_ZONE')
# Github ACCESS_TOKEN, API rate limit 5000/H
ACCESS_TOKEN = common_helpers.get_config('ACCESS_TOKEN')
YESTERDAY = date.today() - timedelta(days=1)


def date_generartor():
    """
    generrats query params :since , until
    """
    # UTC time
    today = iso8601.parse_date(date.today().isoformat())
    # 8 hours offset
    tz_offset = timedelta(hours=8)
    # since the very beginning of the yesterday local time(Beijing, China)
    # for debug purpose, days=60 will be changed to 1 later
    since = today - timedelta(days=1) - tz_offset
    # until the last secs of the yesterday local time(Beijing, China)
    until = today - timedelta(seconds=1) - tz_offset
    return since, until


def utc2local_parser(date):
    """
    load utc date string into local(Beijing) date ojetcs.
    """
    return iso8601.parse_date(date).astimezone(pytz.timezone(TIME_ZONE))


def _create_comments(comments, comment_type, pull_db, members):
    """
    creates comments of a pull.
    type 0 : comments
    type 1 : review comments
    """
    for comment in comments:
        # comments that commented by members are count.
        if comment['user']['login'] in [member.github_account for member in members]:
            if Comment.objects.is_exist(comment['id']):
                pass
                # comment_db = Comment.objects.get(comment_id=comment['id'])
                # comment_db.body = comment['body']
                # comment_db.updated_at = str(utc2local_parser(
                #     comment['updated_at']))[:-6]
                # comment_db.save()
            else:
                Comment.objects.create(comment_id=comment['id'],
                                       author=comment['user']['login'],
                                       comment_type=comment_type,
                                       body=comment['body'],
                                       created_at=str(utc2local_parser(
                                           comment['created_at']))[:-6],
                                       updated_at=str(utc2local_parser(
                                           comment['updated_at']))[:-6],
                                       pull=pull_db
                                       )


@dbtransaction.atomic
def auto_load_pulls():
    """
    load the latest page of pull request and its comments into database.
    """
    logger.info('[CRON] auto_load_pulls on date %s start.' % YESTERDAY)
    members = Member.objects.all()
    repositories_db = Repository.objects.all()  # from database

    for repository_db in repositories_db:
        print repository_db
        repo = Repo(repository_db.owner, repository_db.repo)
        # due to can not get pulls by date, everyday get latest 120.
        pulls = repo.get_pulls(page=4, access_token=ACCESS_TOKEN)
        for pull in pulls:
            # retrive all the pull request, update on 23/05/17.
            # if pull['user']['login'] in [member.github_account for member in members]:
            # current pull request based on number.
            pull = repo.get_pull_by_number(
                number=pull['number'], access_token=ACCESS_TOKEN)

            if pull['state'] == 'closed':
                pull['state'] = 0
            if pull['state'] == 'open':
                pull['state'] = 1
            if pull['closed_at'] is not None:
                pull['closed_at'] = str(
                    utc2local_parser(pull['closed_at']))[:-6]

            if Pull.objects.is_exist(pull['number'], repository_db):
                # auto_load_pulls will not update pulls,left to auto_change_pull_state.
                pass
            else:
                logger.info('[CRON] auto_load_pulls creating new pull in db on date %s start.' % YESTERDAY)
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
                                              created_at=str(utc2local_parser(
                                                  pull['created_at']))[:-6],
                                              updated_at=str(utc2local_parser(
                                                  pull['updated_at']))[:-6],
                                              closed_at=pull['closed_at'],
                                              repository=repository_db
                                              )

                if pull_db.comments > 0:
                    # create issue's comments in db if it exists, witch is type
                    # 0
                    comments = repo.get_issue_comments(pull['number'], access_token=ACCESS_TOKEN)
                    _create_comments(comments, 0, pull_db, members)

                if pull_db.review_comments > 0:
                    # create pull's comments in db if it exists, witch is type
                    # 1
                    comments = repo.get_pull_comments(pull['number'], access_token=ACCESS_TOKEN)
                    _create_comments(comments, 1, pull_db, members)

    logger.info('[CRON] auto_load_pulls on date %s done.' % YESTERDAY)


# todo discuss later
@dbtransaction.atomic
def auto_retrieve_bug_id():
    """
    load bug id into pull if pull.bug_id is null
    """
    logger.info('[CRON] auto_retrieve_bug_id on date %s start.' % YESTERDAY)
    # after 14 days will not try to find the bug id, beacuse it was missing
    days_ago = date.today() - timedelta(days=14)
    pulls_db = Pull.objects.filter(
        bug_id=None, created_at__gt=days_ago)
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
            comments_db = Comment.objects.filter(
                pull=pull_db, comment_type=0, author=pull_db.author)
            for comment_db in comments_db:
                text = comment_db.body.encode("utf-8")
                match = regex.search(text)
                if match:
                    bug_id = re.findall(r"\d+", match.groups()[0])[0]

        pull_db.bug_id = bug_id
        pull_db.save()
    logger.info('[CRON] auto_retrieve_bug_id on date %s done' % YESTERDAY)


# todo change pull state when it is closed, or updated
# also need to change stats eg. commits, additions..
# after PR created, new comments and review comments will be add into db,
# when PR was updated.
@dbtransaction.atomic
def auto_change_pull_state():
    """
    change pull state when it is closed or updated
    """
    # pull requests are still open
    logger.info('[CRON] auto_change_pull_state on date %s start' % YESTERDAY)
    members = Member.objects.all()
    pulls_db = Pull.objects.filter(pull_state=1)
    for pull_db in pulls_db:
        # call github api
        repo = Repo(pull_db.repository.owner, pull_db.repository.repo)
        pull = repo.get_pull_by_number(
            number=pull_db.pull_number, access_token=ACCESS_TOKEN)

        if ((pull_db.updated_at != datetime.strptime(
                str(utc2local_parser(
                    pull['updated_at']))[:-6], '%Y-%m-%d %H:%M:%S')) and (pull['state'] == 'open')):
            # if a pull request is updated, it could have new comments or commits
            # update pull info in db
            logger.info('[CRON] auto_change_pull_state update pull in db on date %s start' % YESTERDAY)
            pull_db.body = pull['body']
            pull_db.pull_merged = pull['merged']
            pull_db.comments = pull['comments']
            pull_db.review_comments = pull['review_comments']
            pull_db.commits = pull['commits']
            pull_db.additions = pull['additions']
            pull_db.deletions = pull['deletions']
            pull_db.changed_files = pull['changed_files']
            pull_db.updated_at = str(utc2local_parser(pull['updated_at']))[:-6]
            pull_db.save()

            # create new comments of when updating pull reuqest
            def _create_newly_added_comments():
                comments_db = Comment.objects.filter(pull=pull_db)
                if pull_db.comments > 0:
                    # create issue's comments in db if it exists, witch is type
                    # 0
                    comments = repo.get_issue_comments(pull['number'], access_token=ACCESS_TOKEN)
                    new_comments = (set([comment['id'] for comment in comments]) -
                                    set([comment_db.comment_id for comment_db in comments_db]))
                    for comment in comments:
                        if comment['id'] in new_comments:
                            _create_comments(comments, 0, pull_db, members)

                if pull_db.review_comments > 0:
                    # create pull's comments in db if it exists, witch is type
                    # 1
                    comments = repo.get_pull_comments(pull['number'], access_token=ACCESS_TOKEN)
                    new_comments = (set([comment['id'] for comment in comments]) -
                                    set([comment_db.comment_id for comment_db in comments_db]))
                    for comment in comments:
                        if comment['id'] in new_comments:
                            _create_comments(comments, 1, pull_db, members)

            _create_newly_added_comments()

        if pull['state'] == 'closed':
            logger.info('[CRON] auto_change_pull_state close pull in db on date %s start' % YESTERDAY)
            # if cloesed, change state and create new comments.
            pull_db.body = pull['body']
            pull_db.pull_state = 0
            pull_db.pull_merged = pull['merged']
            pull_db.comments = pull['comments']
            pull_db.review_comments = pull['review_comments']
            pull_db.commits = pull['commits']
            pull_db.additions = pull['additions']
            pull_db.deletions = pull['deletions']
            pull_db.changed_files = pull['changed_files']
            pull_db.updated_at = str(utc2local_parser(pull['updated_at']))[:-6]
            pull_db.closed_at = str(utc2local_parser(pull['closed_at']))[:-6]
            pull_db.save()

            _create_newly_added_comments()

    logger.info('[CRON] auto_change_pull_state on date %s done' % YESTERDAY)

# =================================
# auto_load_commits_of_members()
# auto_load_issues()
# auto_load_pulls()
# auto_retrieve_bug_id()
# auto_change_pull_state()
