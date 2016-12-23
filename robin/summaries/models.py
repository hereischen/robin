from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from commons.models import Timestampable


# Create your models here.
class Weekly(Timestampable, models.Model):
    """
    Defines fields of weekly summary for pulls
    """
    from_date = models.DateTimeField(verbose_name='from date')
    to_date = models.DateTimeField(verbose_name='to_date')
    week_number = models.CharField(max_length=16, unique=True, verbose_name='week bumber')
    summary_type = models.CharField(max_length=16,verbose_name='summary type')
    number_of_pulls = models.PostiveIntegerField(default=0, verbose_name='number of pulls')

    class Meta:
        verbose_name = _('weekly_summary')
        verbose_name_pluarl = _('weekly_summaries')

    def __unicode__(self):
        return str(self.week_number)

