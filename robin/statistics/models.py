from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import json as jsonfield
from commons.models import Timestampable


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


class Issue(Timestampable, models.Model):
    """
    Defines fields of an issue.
    """
    issue_number = models.IntegerField(unique=True, verbose_name='issue number')
    tittle = models.CharField(max_length=256, verbose_name='issue tittle')
    issue_by = models.CharField(max_length=32, verbose_name='issue by')
    state = models.CharField(verbose_name='state')  # may need to change to choice field with const choices.
    body = models.TextField(verbose_name='issue body')
    merged = models.BooleanField(default=False, verbose_name='is_pull_merged')  # may need to be combined into state

    comments = models.IntegerField(default=0, verbose_name='comments')  # !!!
    commits = models.IntegerField(default=0, verbose_name='commits')  # !!!

    addition = models.IntegerField(default=0, verbose_name='commits addition')
    deletions = models.IntegerField(default=0, verbose_name='commits deletions')
    changed_files = models.IntegerField(default=0, verbose_name='changed files ')

    created_at = models.DateTimeField(verbose_name='issue created date')
    updated_at = models.DateTimeField(verbose_name='issue uodated date')
    closed_at = models.DateTimeField(verbose_name='issue closed date')

    # comments = jsonfield.JSONField(verbose_name=u'issue comments')
    # ForeignKeys:
    # decide later

    class Meta:
        verbose_name = _('issue')
        verbose_name_plural = _('issues')

    def __unicode__(self):
        return self.issue_number


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
    # need to be decide later
    repository = models.ForeignKey('Repository', verbose_name='repository')
    issue = models.ForeignKey('Issue', verbose_name='issue')

    class Meta:
        verbose_name = _('commit')
        verbose_name_plural = _('commits')

    def __unicode__(self):
        return self.sha

    # def save(self, **kwargs):
    #     pass
    # to do, covert datetime
    # self.date = _covert_to_utc(self.utc)
    # super(Commit, self).save(kwargs)


class Comments(Timestampable, models.Model):
    """
    Defines fields of a comment.
    """
    comment_id = models.IntegerField(unique=True, verbose_name='comment id')
    author = models.CharField(max_length=32, verbose_name='comment author')  # github login
    body = models.TextField(verbose_name='comment body')
    created_at = models.DateTimeField(verbose_name='comment created date')
    updated_at = models.DateTimeField(verbose_name='comment uodated date')

    # ForeignKeys:
    # need to be decide later

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    def __unicode__(self):
        return self.comment_id
