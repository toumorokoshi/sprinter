"""
The egg formula will install scripts from an egg (including dependencies) into a sandboxed directory.
[eggs]
formula = sprinter.formulas.egg
egg = sprinter
eggs = pelican, pelican-gist
       jedi, epc
links = http://github.com/toumorokoshi/sprinter/tarball/master#egg=sprinter-0.6
redownload = true
"""
from __future__ import unicode_literals
import os
import re

import sprinter.lib as lib
from sprinter.formulabase import FormulaBase
from sprinter.virtualenv import create_environment as create_virtualenv

# a list of regex's that should no be symlinked to the bin path
BLACKLISTED_EXECUTABLES = [
    "^python.*$",
    "^easy_install.*$",
    "^activate.*$",
    "^pip.*$"]


class EggscriptFormula(FormulaBase):

    valid_options = FormulaBase.valid_options + ['egg', 'eggs', 'redownload']

    def install(self):
        create_virtualenv(self.directory.install_directory(self.feature_name))
        self.__install_eggs(self.target)
        self.__add_paths(self.target)
        return FormulaBase.install(self)

    def update(self):
        if (self.source.get('egg', '') != self.target.get('egg', '') or
            self.source.get('eggs', '') != self.target.get('eggs', '') or
            (self.target.has('redownload') and self.target.is_affirmative('redownload'))):
                self.__install_eggs(self.target)
        self.__add_paths(self.target)
        return FormulaBase.update(self)

    def validate(self):
        if self.target:
            if not (self.target.has('egg') or self.target.has('eggs')):
                self.logger.warn("No eggs will be installed! 'egg' or 'eggs' parameter not set!")
        return FormulaBase.validate(self)
                
    def __install_eggs(self, config):
        """ Install eggs for a particular configuration """
        eggs = []
        if config.has('egg'):
            eggs += [config.get('egg')]
        if config.has('eggs'):
            eggs += [egg.strip() for egg in re.split(',|\n', config.get('eggs'))]
        self.logger.debug("Installing eggs %s..." % eggs)
        with open(os.path.join(self.directory.install_directory(self.feature_name), 'requirements.txt'),
                  'w+') as fh:
            fh.write('\n'.join(eggs))
        lib.call("bin/pip install -r requirements.txt --upgrade",
                 cwd=self.directory.install_directory(self.feature_name))

    def __add_paths(self, config):
        """ add the proper resources into the environment """
        bin_path = os.path.join(self.directory.install_directory(self.feature_name), 'bin')
        for f in os.listdir(bin_path):
            symlink = True
            for pattern in BLACKLISTED_EXECUTABLES:
                if re.match(pattern, f):
                    symlink = False
            if symlink:
                self.directory.symlink_to_bin(f, os.path.join(bin_path, f))
