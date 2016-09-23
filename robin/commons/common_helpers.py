import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_config(name, config_default=None):
    """
    Get configuration variable from environment variable
    or django setting.py
    """
    config = os.environ.get(name, getattr(settings, name, config_default))
    if config is not None:
        return config
    else:
        raise ImproperlyConfigured("Can't find config for '%s' either in environment"
                                   "variable or in settings.py" % name)
