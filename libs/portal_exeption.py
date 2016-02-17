# -*- coding: utf-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""


class PException(Exception):
    def __str__(self):
        return '[Portal Exception] %s' % Exception.__str__(self)


class PForbidden(PException):
    def __str__(self):
        return '[Portal Forbidden Exception] %s' % Exception.__str__(self)