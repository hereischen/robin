import os
from .base import *

DEBUG = True

ALLOWED_HOSTS = []

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
KEY_ROOT = os.path.join(BASE_DIR, 'keys')

SERVER_ALIAS = 'local'

CRONTAB_DJANGO_SETTINGS_MODULE = 'robin.settings.local'

with open(os.path.join(KEY_ROOT, 'access_token.txt')) as f:
    ACCESS_TOKEN = f.read().strip()
