from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
# from django_extensions.db.fields import json as jsonfield
from commons.models import Timestampable

# pull state code
STATE = (
    (0, 'CLOSED'),
    (1, 'OPEN'),
)

# comment type
COMMENT_TYPE = (
    (0, 'COMMENTS'),
    (1, 'REVIEW COMMENTS'),
)


class Repository(Timestampable, models.Model):
    """
    Defines fields of a repository.
    """
    owner = models.CharField(max_length=32, verbose_name='repository owner')
    repo = models.CharField(max_length=32, verbose_name='repository name')

    class Meta:
        verbose_name = _('repository')
        verbose_name_plural = _('repositories')
        unique_together = ('owner', 'repo')

    def __unicode__(self):
        return ('/'.join([self.owner, self.repo]))


class Pull(Timestampable, models.Model):
    """
    Defines fields of an PullRequest.
    """
    pull_number = models.IntegerField(unique=True, verbose_name='pull request number')
    title = models.CharField(max_length=256, verbose_name='pull request title')
    author = models.CharField(max_length=32, verbose_name='pull request by')

    body = models.TextField(verbose_name='pull request body')
    bug_id = models.CharField(max_length=32, null=True, verbose_name='bug id')

    pull_state = models.PositiveSmallIntegerField(default=1, choices=STATE, verbose_name='pull state')
    pull_merged = models.BooleanField(default=False, verbose_name='is pull merged')

    comments = models.IntegerField(default=0, verbose_name='comments')
    review_comments = models.IntegerField(default=0, verbose_name='review_comments')
    commits = models.IntegerField(default=0, verbose_name='commits')

    additions = models.IntegerField(default=0, verbose_name='commits additions')
    deletions = models.IntegerField(default=0, verbose_name='commits deletions')
    changed_files = models.IntegerField(default=0, verbose_name='changed files ')

    created_at = models.DateTimeField(verbose_name='pull request created date')
    updated_at = models.DateTimeField(verbose_name='pull request uodated date')
    closed_at = models.DateTimeField(null=True, verbose_name='pull request closed date')

    # comments = jsonfield.JSONField(verbose_name=u'issue comments')
    # ForeignKeys:
    repository = models.ForeignKey('Repository', verbose_name='repository')

    class Meta:
        verbose_name = _('pull_request')
        verbose_name_plural = _('pull_requests')

    def __unicode__(self):
        return str(self.pull_number)


class Commit(Timestampable, models.Model):
    """
    Defines fields of a commit.
    """
    sha = models.CharField(max_length=64, unique=True, db_index=True, verbose_name='git commit sha')
    author = models.CharField(max_length=32, verbose_name='commit author')  # github login
    email = models.EmailField(verbose_name='commit email')
    date = models.DateTimeField(verbose_name='commit date')
    # utc_date = models.DateTimeField(verbose_name='commit UTC date')
    message = models.TextField(verbose_name='commit message')

    # ForeignKeys:
    repository = models.ForeignKey('Repository', verbose_name='repository')
    # In commits, this field can be null,due to a commit can not relate to any issues
    pull = models.ForeignKey('Pull', null=True, verbose_name='pull request')

    class Meta:
        verbose_name = _('commit')
        verbose_name_plural = _('commits')

    def __unicode__(self):
        return self.sha


class Comment(Timestampable, models.Model):
    """
    Defines fields of a comment.
    """
    comment_id = models.IntegerField(unique=True, verbose_name='comment id')
    comment_type = models.PositiveSmallIntegerField(default=1, choices=COMMENT_TYPE, verbose_name='comment type')
    author = models.CharField(max_length=32, verbose_name='comment author')  # github login
    body = models.TextField(verbose_name='comment body')
    created_at = models.DateTimeField(verbose_name='comment created date')
    updated_at = models.DateTimeField(verbose_name='comment uodated date')

    # ForeignKeys:
    pull = models.ForeignKey('Pull', null=True, verbose_name='pull request')

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    def __unicode__(self):
        return str(self.comment_id)
