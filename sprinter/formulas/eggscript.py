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

    def install(self, feature_name, config):
        self.bp = BuildoutPuppet(root_path=self.directory.install_directory(feature_name))
        self.__install_eggs(config)
        self.__add_paths(config)
        super(EggscriptFormula, self).install(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        self.bp = BuildoutPuppet(root_path=self.directory.install_directory(feature_name))
        if (source_config.get('egg', None) != target_config.get('egg', None) or
            source_config.get('eggs', None) != target_config.get('eggs', None) or
            lib.is_affirmative(target_config.get('redownload'))):
                self.__install_eggs(target_config)
        self.__add_paths(target_config)
        super(EggscriptFormula, self).update(feature_name, source_config, target_config)

    def __install_eggs(self, config):
        """ Install eggs for a particular configuration """
        eggs = []
        if 'egg' in config:
            eggs += [config['egg']]
        if 'eggs' in config:
            eggs += [egg.strip() for egg in re.split(',|\n', config['eggs'])]
        self.bp.eggs = self.eggs = eggs
        self.bp.links = [link.strip() for link in re.split(',|\n', config.get('links', ''))]
        if lib.is_affirmative(config.get('redownload', 'false')):
            self.logger.debug("Removing eggs %s..." % eggs)
        self.logger.debug("Installing eggs %s..." % eggs)
        self.bp.install()

    def __add_paths(self, config):
        """ add the proper resources into the environment """
        self.directory.add_to_rc("export PATH=%s:$PATH\n" % self.bp.bin_path())
