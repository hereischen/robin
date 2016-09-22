from __future__ import unicode_literals

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


class Member(Timestampable, models.Model):
    """
    Defines fields of a member.
    """
    name = models.CharField(max_length=32, unique=True, db_index=True, verbose_name='member name')
    kerbroes_id = models.CharField(max_length=32, unique=True, verbose_name='Kerbroes ID')
    rh_email = models.EmailField(unique=True, verbose_name='RedHat email')
    github_account = models.CharField(max_length=32, unique=True, verbose_name='GitHub account')
    team = models.ForeignKey('Team', verbose_name=u'team')

    class Meta:
        verbose_name = _('member')
        verbose_name_plural = _('members')

    def __unicode__(self):
        return self.kerbroes_id

    def save(self, **kwargs):
        self.rh_email = '@'.join([self.kerbroes_id, 'redhat.com'])
        super(Member, self).save(kwargs)
