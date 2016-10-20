from .base import *

DEBUG = False

ALLOWED_HOSTS = []

STATIC_ROOT = '/home/hachen/resources/static/robin'

SERVER_ALIAS = 'test'

CRONTAB_DJANGO_SETTINGS_MODULE = 'robin.settings.test'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'robin',
        'USER': 'root',
        'PASSWORD': 'redhat1qaz@WSX',
        'HOST': '10.66.8.100',
        'PORT': '3306',
        # Set this to True to wrap each HTTP request in a transaction on this
        # database.
        'ATOMIC_REQUESTS': True,
    },
}
