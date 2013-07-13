"""
The egg formula will install scripts from an egg (including dependencies) into a sandboxed directory.
[eggs]
formula = sprinter.formulas.egg
egg = sprinter
eggs = pelican, pelican-gist
       jedi, epc
include-scripts = true
include-eggs = false
links = http://github.com/toumorokoshi/sprinter/tarball/master#sprinter-0.6
"""
import logging
import os
import re

import requests

from sprinter import lib
from sprinter.formulabase import FormulaBase
from sprinter.exceptions import CommandMissingException

BOOTSTRAP_URL = "http://downloads.buildout.org/2/bootstrap.py"

BASE_CONFIG = """
[buildout]
parts = python

find-links = %(find-links)s

[python]
recipe = zc.recipe.egg
eggs = %(eggs)s
"""


class EggFormula(FormulaBase):

    def install(self, feature_name, config):
        self.bp = BuildoutPuppet(root_path="~/.sprinter/sprinter")
        self.__install_eggs(config)
        self.__add_paths(config)
        super(EggFormula, self).install(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        self.bp = BuildoutPuppet(root_path="~/.sprinter/sprinter")
        if (source_config.get('egg', None) != target_config.get('egg', None) or
           source_config.get('eggs', None) != target_config.get('eggs', None)):
            self.__install_eggs(target_config)
        self.__add_paths(target_config)
        super(EggFormula, self).update(feature_name, source_config, target_config)

    def __install_eggs(self, config):
        """ Install eggs for a particular configuration """
        eggs = []
        if 'egg' in config:
            eggs += [config['egg']]
        if 'eggs' in config:
            eggs += [egg.strip() for egg in re.split(',|\n', config['eggs'])]
        self.bp.eggs = self.eggs = eggs
        self.bp.links = [link.strip() for link in re.split(',|\n', config['links'])]
        self.logger.debug("Installing eggs %s..." % eggs)
        self.bp.install()

    def __add_paths(self, config):
        """ add the proper resources into the environment """
        rc_script = ""
        if self.lib.is_affirmative(config.get('include-scripts', 'false')):
            rc_script += "export PATH=%s:$PATH\n" % self.bp.bin_path()
        if self.lib.is_affirmative(config.get('include-eggs', 'true')):
            PYTHONPATH = ""
            for egg in os.listdir(self.bp.egg_path()):
                PYTHONPATH += os.path.join(self.bp.egg_path(), egg) + ":"
                rc_script += "export PYTHONPATH=%s$PYTHONPATH\n" % PYTHONPATH
        self.directory.add_to_rc(rc_script)
        

class BuildoutPuppet(object):
    """ A wrapper class to control buildout programatically """

    def __init__(self, root_path, eggs=[]):
        self.root_path = os.path.expanduser(root_path)
        self.buildout_path = os.path.join(self.root_path, 'buildout.cfg')
        self.options = []
        self.eggs = eggs
        self.links = []

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

    def download_bootstrap(self):
        """ Install buildout to the path provided """
        bootstrap_path = os.path.join(self.root_path, "bootstrap.py")
        if not os.path.exists(bootstrap_path):
            with open(bootstrap_path, 'w+') as fh:
                fh.write(requests.get(BOOTSTRAP_URL).content)

    def write_buildout(self):
        """ Write buildout.cfg to the path provided """
        d = {'eggs':       "\n       ".join(self.eggs),
             'find-links': "\n       ".join(self.links)}
        with open(self.buildout_path, 'w+') as fh:
            fh.write(BASE_CONFIG % d)

    def run_buildout(self):
        """ Run bootstrap.py and bin/buildout """
        lib.call("python bootstrap.py", cwd=self.root_path)
        lib.call("bin/buildout", cwd=self.root_path)
