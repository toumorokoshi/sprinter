import logging
import os
import shutil
import requests
from sprinter import lib

BOOTSTRAP_URL = "http://downloads.buildout.org/2/bootstrap.py"

LOGGER = logging.getLogger('sprinter')

BASE_CONFIG = """
[buildout]
parts = python

find-links = %(find-links)s

[python]
recipe = zc.recipe.egg
eggs = %(eggs)s
"""


class BuildoutPuppet(object):
    """ A wrapper class to control buildout programatically """

    def __init__(self, root_path, eggs=[], logger=LOGGER):
        self.root_path = os.path.expanduser(root_path)
        self.buildout_path = os.path.join(self.root_path, 'buildout.cfg')
        self.options = []
        self.eggs = eggs
        self.links = []
        self.logger = logger

    def install(self):
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)
        self.download_bootstrap()
        self.write_buildout()
        self.run_buildout()

    def bin_path(self):
        """ Return the path to the executable directory """
        return os.path.join(self.root_path, "bin")

    def egg_path(self):
        """ Return the path to the eggs directory """
        return os.path.join(self.root_path, "eggs")

    def clear_eggs(self):
        """ remove the eggs installed """
        for egg in os.listdir(self.egg_path()):
            try:
                shutil.rmtree(os.path.join(self.egg_path(), egg))
            except OSError:
                self.logger.error("Unable to remove egg %s" % egg)

    def download_bootstrap(self):
        """ Install buildout to the path provided """
        bootstrap_path = os.path.join(self.root_path, "bootstrap.py")
        if not os.path.exists(bootstrap_path):
            with open(bootstrap_path, 'w+') as fh:
                fh.write(requests.get(BOOTSTRAP_URL).content)

    def write_buildout(self):
        """ Write buildout.cfg to the path provided """
        d = {'eggs': "\n       ".join(self.eggs),
             'find-links': "\n       ".join(self.links)}
        with open(self.buildout_path, 'w+') as fh:
            fh.write(BASE_CONFIG % d)

    def run_buildout(self):
        """ Run bootstrap.py and bin/buildout """
        lib.call("python -S bootstrap.py", cwd=self.root_path)
        lib.call("bin/buildout", cwd=self.root_path)
