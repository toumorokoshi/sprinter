import httpretty
from sprinter.environment import populate_formula_instance

"""
[noformula]
blank = thishasnoformula
"""


class TestEnvironmentDecorators(object):
    """ Tests for the environment decorators """
