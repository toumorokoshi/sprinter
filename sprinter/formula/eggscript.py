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
import logging
import os
import re

import requests

from sprinter import lib
from sprinter.formulabase import FormulaBase
from sprinter.exceptions import CommandMissingException
from sprinter.buildoutpuppet import BuildoutPuppet


class EggscriptFormula(FormulaBase):

    def install(self):
        self.bp = BuildoutPuppet(
            root_path=self.directory.install_directory(self.feature_name))
        self.__install_eggs(self.target)
        self.__add_paths(self.target)
        return super(EggscriptFormula, self).install()

    def update(self):
        self.bp = BuildoutPuppet(
            root_path=self.directory.install_directory(self.feature_name))
        if (self.source.get('egg', '') != self.target.get('egg', '') or

            self.source.get('eggs', '') != self.target.get('eggs', '') or
            lib.is_affirmative(self.target.get('redownload', 'false'))):
                    self.__install_eggs(self.target)
        self.__add_paths(self.target)
        return super(EggscriptFormula, self).update()

    def validate(self):
        if self.target:
            if not (self.target.has('egg') or self.target.has('eggs')):
                self.logger.warn("No eggs will be installed! 'egg' or 'eggs' parameter not set!")
        return []
                
    def __install_eggs(self, config):
        """ Install eggs for a particular configuration """
        eggs = []
        if config.has('egg'):
            eggs += [config.get('egg')]
        if config.has('eggs'):
            eggs += [egg.strip() for egg in re.split(',|\n', config.get('eggs'))]
        self.bp.eggs = self.eggs = eggs
        self.bp.links = [link.strip() for link in re.split(',|\n', config.get('links', ''))]
        if lib.is_affirmative(config.get('redownload', 'false')):
            self.logger.debug("Removing eggs %s..." % eggs)
            self.bp.delete_eggs()
        self.logger.debug("Installing eggs %s..." % eggs)
        self.bp.install()

    def __add_paths(self, config):
        """ add the proper resources into the environment """
        self.directory.add_to_rc("export PATH=%s:$PATH\n" % self.bp.bin_path())
