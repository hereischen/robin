from .base import *

DEBUG = True

ALLOWED_HOSTS = []

KEY_ROOT = '/Users/hereischen/keys/'

SERVER_ALIAS = 'local'

CRONTAB_DJANGO_SETTINGS_MODULE = 'robin.settings.local'

with open(KEY_ROOT + 'access_token.txt') as f:
    ACCESS_TOKEN = f.read().strip()
