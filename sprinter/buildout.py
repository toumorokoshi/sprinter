"""
Sprinter wrapper to puppet buildout
"""
import os
from zc.buildout import Buildout

BASE_CONFIG = """
[buildout]
"""


class BuildoutPuppet(object):
    """ A wrapper class to control buildout programatically """

    def __init__(self, root_path):
        with open(os.path.join(root_path, 'buildout.cfg'), 'w+') as fh:
            fh.write(BASE_CONFIG)
        self.buildout = Buildout(BASE_CONFIG)
        self.buildout.install()
