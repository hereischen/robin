# -*- coding: utf-8 -*-


class APIError(Exception):
    INVALID_REQUEST_DATA = 101
    INVALID_REQUEST_METHOD = 102
    INVALID_STATUS_DATA = 103
    UNKNOWN_ERROR = 999

    CODE_MESSAGE = {
        INVALID_REQUEST_DATA: 'Invalid Data Provided',
        INVALID_REQUEST_METHOD: 'Invalid Request Method',
        INVALID_STATUS_DATA: 'Invalid Status Data',
        UNKNOWN_ERROR: 'Unknown Error'
    }

    def __init__(self, code, detail=None):
        self.code = code
        self.message = self.CODE_MESSAGE.get(code, '')
        self.detail = detail

    def __str__(self):
        return '%s: %s (%s)' % (self.code, self.message, self.detail)
