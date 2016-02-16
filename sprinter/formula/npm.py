"""
Maintains an npm package

[config]
inputs = git_root==~/code/project

[ssh]
formula = sprinter.formula.npm
npm_root = %(config:git_root)s
node_version = 4.3.0
list_outdated = true
redirect_stdout_to_log = false
"""
from __future__ import unicode_literals

import os
import subprocess
import shutil

from sprinter.formula.base import FormulaBase
from sprinter.exceptions import FormulaException
import sprinter.lib as lib


class NPMFormulaException(FormulaException):
    pass


class NPMFormula(FormulaBase):

    required_options = FormulaBase.required_options + ['npm_root']
    valid_options = FormulaBase.valid_options + ['list_outdated', 'node_version']

    def install(self):
        npm_root = self.target.get('npm_root')
        modules_dir = os.path.join(npm_root, 'node_modules')

        if os.path.exists(modules_dir):
            shutil.rmtree(modules_dir)

        self.__run_command('install', self.target)

        if self.target.has('node_version'):
            self.directory.add_to_env(self.__nvm_use(config=self.target))

        FormulaBase.install(self)

    def update(self):
        source_npm_root = self.source.get('npm_root')
        target_npm_root = self.target.get('npm_root')
        modules_dir = os.path.join(target_npm_root, 'node_modules')

        if target_npm_root != source_npm_root or not os.path.exists(modules_dir):
            return self.install()

        self.__run_command('update', self.target)

        if self.target.has('node_version'):
            self.directory.add_to_env(self.__nvm_use(config=self.target))

        if self.target.is_affirmative('list_outdated'):
            self.__run_command('outdated', self.target)

        return FormulaBase.update(self)

    def activate(self):
        namespace = self.target.get('namespace')
        npm_root = self.target.get('npm_root')
        modules_dir = os.path.join(npm_root, 'node_modules')
        modules_restore = os.path.join(npm_root, 'node_modules.{ns}'.format(ns=namespace))
        modules_bak = os.path.join(npm_root, 'node_modules.sv')

        if os.path.exists(modules_dir):
            if os.path.exists(modules_bak):
                shutil.rmtree(modules_bak)
            shutil.move(modules_dir, modules_bak)
        shutil.move(modules_restore, modules_dir)
        FormulaBase.activate(self)

    def deactivate(self):
        namespace = self.target.get('namespace')
        npm_root = self.target.get('npm_root')
        modules_dir = os.path.join(npm_root, 'node_modules')
        modules_save = os.path.join(npm_root, 'node_modules.{ns}'.format(ns=namespace))

        if os.path.exists(modules_save):
            shutil.rmtree(modules_save)
        shutil.move(modules_dir, modules_save)
        FormulaBase.deactivate(self)

    def __nvm_use(self, config):
        if not config.has('node_version'):
            return ''
        return 'nvm use {version}'.format(
            version=config.get('node_version'))

    def __run_command(self, command, config):
        npm_root = config.get('npm_root')
        shell = False
        # using depth 0, even though it's the default, to minimize npm's tree output

        if config.has('node_version'):
            nvm_command = '{cmd} && '.format(cmd=self.__nvm_use(config=config))
            shell = True
        full_command = "{pre}npm {cmd} --depth 0".format(pre=nvm_command, cmd=command)
        # self.logger.debug("Running {cmd}...".format(cmd=full_command))
        stdout = subprocess.PIPE if config.is_affirmative('redirect_stdout_to_log', 'true') else None
        return_code, output = lib.call(full_command, shell=shell, stdout=stdout, cwd=npm_root)
        if config.is_affirmative('fail_on_error', True) and return_code != 0:
            raise NPMFormulaException("npm returned a return code of {0}!".format(return_code))
        return True
