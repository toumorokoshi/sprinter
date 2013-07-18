"""
The egg formula will install scripts from an egg (including dependencies) into a sandboxed directory.
[eggs]
formula = sprinter.formulas.eggscript
egg = sprinter
eggs = pelican, pelican-gist
       jedi, epc
"""
import os
import re

from sprinter import lib
from sprinter.formulabase import FormulaBase
from sprinter.virtualenv import create_environment as create_virtualenv

# a list of regex's that should no be symlinked to the bin path
BLACKLISTED_EXECUTABLES = [
    "^python.*$",
    "^easy_install.*$",
    "^activate.*$",
    "^pip.*$"]


class EggscriptFormula(FormulaBase):

    def install(self, feature_name, config):
        create_virtualenv(self.directory.install_directory(feature_name))
        self.__install_eggs(feature_name, config)
        self.__add_paths(feature_name, config)
        return FormulaBase.install(self, feature_name, config)

    def update(self, feature_name, source_config, target_config):
        self.__install_eggs(feature_name, target_config)
        self.__add_paths(feature_name, target_config)
        return FormulaBase.update(self, feature_name, source_config, target_config)

    def __install_eggs(self, feature_name, config):
        """ Install eggs for a particular configuration """
        eggs = []
        if config.has('egg'):
            eggs += [config.get('egg')]
        if config.has('eggs'):
            eggs += [egg.strip() for egg in re.split(',|\n', config.get('eggs'))]
        self.logger.debug("Installing eggs %s..." % eggs)
        with open(os.path.join(self.directory.install_directory(feature_name), 'requirements.txt'),
                  'w+') as fh:
            fh.write('\n'.join(eggs))
        lib.call("bin/pip install -r requirements.txt --upgrade",
                 cwd=self.directory.install_directory(feature_name))

    def __add_paths(self, feature_name, config):
        """ add the proper resources into the environment """
        bin_path = os.path.join(self.directory.install_directory(feature_name), 'bin')
        for f in os.listdir(bin_path):
            symlink = True
            for pattern in BLACKLISTED_EXECUTABLES:
                if re.match(pattern, f):
                    symlink = False
            if symlink:
                self.directory.symlink_to_bin(f, os.path.join(bin_path, f))
