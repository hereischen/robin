# -*- coding: utf-8 -*-
import logging
from django.shortcuts import render
from . import (VERSION, RELEASE_DATE)

logger = logging.getLogger(__name__)


def home(request):
    """
    renders home page and set resp heades for deployment check
    """
    if request.method == 'GET':
        logger.info('[home] index is visted.')
        resp = render(request, 'index.html', {})
        resp.setdefault('IGE-Version', VERSION)
        resp.setdefault('IGE-Release-Date', RELEASE_DATE)
        return resp
