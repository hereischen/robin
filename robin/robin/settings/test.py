from .base import *

DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []

STATIC_ROOT = ''

SERVER_ALIAS = 'test'

CRONTAB_DJANGO_SETTINGS_MODULE = 'robin.settings.test'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ.get('DATABASE_HOST', ''),
        'PORT': 8000,
        'NAME': os.environ.get('DATABASE_NAME', ''),
        'USER': os.environ.get('DATABASE_USER', ''),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
    }
}
