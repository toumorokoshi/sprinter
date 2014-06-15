"""
This lists all the exceptions in sprinter
"""
from __future__ import unicode_literals


class SprinterException(Exception):
    """ For generic sprinter exceptions """


class FormulaException(SprinterException):
    """ For a generic exception with a formula """
