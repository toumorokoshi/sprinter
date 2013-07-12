"""
Sprinter wrapper to puppet buildout
"""
import os
from zc.buildout.buildout import Buildout

BASE_CONFIG = """
[buildout]
parts = python

[python]
recipe = zc.recipe.egg
eggs = %(eggs)s
"""


class BuildoutPuppet(object):
    """ A wrapper class to control buildout programatically """

    def __init__(self, root_path):
        self.root_path = os.path.expanduser(root_path)
        self.buildout_path = os.path.join(self.root_path, 'buildout.cfg')
        self.options = []
        self.eggs = []

    def install(self):
        d = {'eggs': "\n       ".join(self.eggs)}
        with open(self.buildout_path, 'w+') as fh:
            fh.write(BASE_CONFIG % d)
        self.buildout = Buildout(self.buildout_path, self.options)
        self.buildout.install([])
