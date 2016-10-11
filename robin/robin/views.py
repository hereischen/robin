# -*- coding: utf-8 -*-
from django.shortcuts import render
from . import (VERSION, RELEASE_DATE)


def home(request):
    """
    renders home page and set resp heades for deployment check
    """
    if request.method == 'GET':
        resp = render(request, 'index.html', {})
        resp.setdefault('IGE-Version', VERSION)
        resp.setdefault('IGE-Release-Date', RELEASE_DATE)
        return resp
