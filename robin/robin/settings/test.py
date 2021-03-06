from .base import *

DEBUG = True

ALLOWED_HOSTS = []

STATIC_ROOT = '/home/hachen/resources/robin/static/'

KEY_ROOT = '/home/hachen/resources/robin/keys/'

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
        'OPTIONS': {'charset': 'utf8mb4'},
    },
}

# Github access_token. API rate limit,
# https://developer.github.com/v3/#rate-limiting
with open(KEY_ROOT + 'access_token.txt') as f:
    ACCESS_TOKEN = f.read().strip()
