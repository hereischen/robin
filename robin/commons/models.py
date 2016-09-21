from __future__ import unicode_literals

from django.db import models


# create and modified date for every item in the database.
class Timestampable(models.Model):
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='create date')
    modified_date = models.DateTimeField(auto_now=True, verbose_name='modified date')

    class Meta:
        abstract = True
