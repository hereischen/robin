from __future__ import unicode_literals
import datetime

from django.db import models
from commons.models import Timestampable
from django.utils.translation import ugettext_lazy as _


class Team(Timestampable, models.Model):
    """
    Defines fields of a team.
    """
    team_name = models.CharField(max_length=32, unique=True, verbose_name='team name')
    team_code = models.CharField(max_length=32, unique=True, verbose_name='team code')

    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')

    def __unicode__(self):
        return self.team_name


class MemberManager(models.Manager):

    def is_serving(self, github_account):
        return True if self.get_queryset().filter(github_account=github_account,
                                                  serving=True
                                                  ) else False


class Member(Timestampable, models.Model):
    """
    Defines fields of a member.
    """
    name = models.CharField(max_length=32, unique=True, db_index=True, verbose_name='member name')
    kerbroes_id = models.CharField(max_length=32, unique=True, verbose_name='Kerbroes ID')
    rh_email = models.EmailField(unique=True, verbose_name='RedHat email')
    github_account = models.CharField(max_length=32, unique=True, verbose_name='GitHub account')
    serving = models.BooleanField(default=True, verbose_name='on the job')
    leave_date = models.DateField(null=True, blank=True, verbose_name='leave date')
    team = models.ForeignKey('Team', related_name='members', verbose_name=u'team')
    objects = MemberManager()

    class Meta:
        verbose_name = _('member')
        verbose_name_plural = _('members')

    def __unicode__(self):
        return self.kerbroes_id

    def save(self, **kwargs):
        self.rh_email = '@'.join([self.kerbroes_id, 'redhat.com'])
        if self.leave_date is None:
            if not self.serving:
                self.leave_date = datetime.date.today()
        super(Member, self).save(kwargs)
