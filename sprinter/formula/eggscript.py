"""
The egg formula will install scripts from an egg (including dependencies) into a sandboxed directory.
[config]
inputs =
    project_root==~/code/my_app

[eggs]
formula = sprinter.formula.egg
egg = file:%(config:project_root)s
eggs = sprinter, pelican, pelican-gist
       jedi, epc
executables = sprinter
links = http://github.com/toumorokoshi/sprinter/tarball/master#egg=sprinter-0.6
redownload = true
"""
from __future__ import unicode_literals
import logging
import os
import re
import subprocess

import sprinter.lib as lib
from sprinter.formula.base import FormulaBase
from sprinter.exceptions import FormulaException
from virtualenv import file_search_dirs, create_environment as create_virtualenv

# a list of regex's that should no be symlinked to the bin path
BLACKLISTED_EXECUTABLES = [
    "^python.*$",
    "^easy_install.*$",
    "^activate.*$",
    "^pip.*$"]


class EggscriptFormulaException(FormulaException):
    pass


class EggscriptFormula(FormulaBase):

    valid_options = FormulaBase.valid_options + [
        'egg', 'eggs', 'redownload', 'fail_on_error', 'executables'
    ]

    def install(self):
        create_virtualenv(self.directory.install_directory(self.feature_name),
                          search_dirs=file_search_dirs(), symlink=True)
        self.__install_eggs(self.target)
        self.__add_paths(self.target)
        return FormulaBase.install(self)

    def update(self):
        acted = False
        if (self.source.get('egg', '') != self.target.get('egg', '') or
            self.source.get('eggs', '') != self.target.get('eggs', '') or
            (self.target.has('redownload') and self.target.is_affirmative('redownload'))):
                self.__install_eggs(self.target)
                acted = True
        self.__add_paths(self.target)
        FormulaBase.update(self)
        return acted

    def validate(self):
        if self.target:
            if not (self.target.has('egg') or self.target.has('eggs')):
                self.logger.warn("No eggs will be installed! 'egg' or 'eggs' parameter not set!")
        return FormulaBase.validate(self)

    def __polish_egg(self, raw_egg):
        egg = raw_egg.strip()
        if egg.startswith('file:'):
            return "-e file://{egg}".format(
                egg=os.path.expanduser(egg.split(':')[-1]))
        else:
            return egg

    def __gather_eggs(self, config):
        eggs = []
        if config.has('egg'):
            eggs.append(self.__polish_egg(config.get('egg')))

        if config.has('eggs'):
            for egg in re.split(',(?!<)|\n', config.get('eggs')):
                eggs.append(self.__polish_egg(egg))
        return eggs

    def __load_carton(self, egg_carton, eggs):
        egg_carton = os.path.join(*egg_carton)
        with open(egg_carton, 'w+') as fh:
            fh.write('\n'.join(eggs))

    def __prepare_eggs(self, egg_carton, config):
        stdout = None
        if config.is_affirmative('redirect_stdout_to_log', 'true'):
            stdout = subprocess.PIPE

        egg_recipe = "PYTHONPATH='' bin/pip install -r {filename} --upgrade".format(filename=egg_carton[1])
        return_code, output = lib.call(egg_recipe,
                                       cwd=egg_carton[0],
                                       output_log_level=logging.DEBUG,
                                       shell=True,
                                       stdout=stdout)
        return return_code

    def __install_eggs(self, config):
        """ Install eggs for a particular configuration """
        egg_carton = (self.directory.install_directory(self.feature_name),
                      'requirements.txt')
        eggs = self.__gather_eggs(config)

        self.logger.debug("Installing eggs %s..." % eggs)
        self.__load_carton(egg_carton, eggs)

        return_code = self.__prepare_eggs(egg_carton, config)

        if config.is_affirmative('fail_on_error', True) and return_code != 0:
            raise EggscriptFormulaException(
                "Egg script {name} returned a return code of {code}!".format(
                    name=self.feature_name, code=return_code))

    def __add_paths(self, config):
        """ add the proper resources into the environment """
        bin_path = os.path.join(self.directory.install_directory(self.feature_name), 'bin')
        whitelist_executables = self._get_whitelisted_executables(config)
        for f in os.listdir(bin_path):
            for pattern in BLACKLISTED_EXECUTABLES:
                if re.match(pattern, f):
                    continue
            if whitelist_executables and f not in whitelist_executables:
                continue
            self.directory.symlink_to_bin(f, os.path.join(bin_path, f))

    @staticmethod
    def _get_whitelisted_executables(config):
        whitelist = config.get("executables", "")
        if not whitelist:
            return None
        return [ex.strip() for ex in re.split(',(?!<)|\n', whitelist)]
