from __future__ import unicode_literals

from commons.models import Timestampable

from django.db import models
from django.utils.translation import ugettext_lazy as _


# summary type
SUMMARY_TYPE = (
    (0, 'REVIEWS'),
    (1, 'SUBMITTED PATCHES'),
    (2, 'UPDATED PATCHES'),
    (3, 'MERGED PATCHES'),
)


# Create your models here.
class Weekly(Timestampable, models.Model):
    """
    Defines fields of weekly summary for pulls
    """
    from_date = models.DateTimeField(verbose_name='from date')
    to_date = models.DateTimeField(verbose_name='to_date')
    # week number eg. 2017w1
    week_number = models.CharField(max_length=16, unique=True,
                                   verbose_name='week number')
    summary_type = models.PositiveSmallIntegerField(default=1,
                                                    choices=SUMMARY_TYPE,
                                                    verbose_name='summary type')
    quantity = models.IntegerField(default=0,
                                   verbose_name='quantity of items')

    class Meta:
        verbose_name = _('weekly_summary')
        verbose_name_plural = _('weekly_summaries')

    def __unicode__(self):
        return str(self.week_number)
