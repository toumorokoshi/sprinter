"""
Maintains an npm package

Can optionally manage nvm versions. When the node_version option is populated,
this formula will add the appropriate `nvm use` call to the .rc for the environment.
If the `node_version` option is set, this formula will clear the node_modules folder
and run a clean `npm install`.

[config]
inputs = git_root==~/code/project

[ssh]
formula = sprinter.formula.npm
npm_root = %(config:git_root)s
node_version = 4.3.0
active_only = true
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
    valid_options = FormulaBase.valid_options + ['list_outdated', 'node_version',
                                                 'active_only']

    def install(self):
        npm_root = self.target.get('npm_root')
        modules_dir = os.path.join(npm_root, 'node_modules')

        if os.path.exists(modules_dir):
            shutil.rmtree(modules_dir)

        if self.target.has('node_version'):
            self.__install_nvm_version()

        self.__run_npm_command('install', self.target)

        if self.target.has('node_version'):
            self.directory.add_to_rc(self.__nvm_use())

        FormulaBase.install(self)

    def update(self):
        source_npm_root = self.source.get('npm_root')
        target_npm_root = self.target.get('npm_root')
        modules_dir = os.path.join(target_npm_root, 'node_modules')
        cur_version = self.source.get('node_version') if self.source.has('node_version') else None
        next_version = self.target.get('node_version') if self.target.has('node_version') else None

        if target_npm_root != source_npm_root or not os.path.exists(modules_dir):
            return self.install()

        if next_version is not None and next_version != cur_version:
            self.__install_nvm_version()
            self.logger.info('Node version change: {cur} to {next}'.format(cur=cur_version, next=next_version))
            self.logger.info('...clearing and re-installing node_modules')
            if os.path.exists(modules_dir):
                shutil.rmtree(modules_dir)

            self.__run_npm_command('install', self.target)
        else:
            self.__run_npm_command('update', self.target)

        if self.target.has('node_version'):
            self.directory.add_to_rc(self.__nvm_use())

        if self.target.is_affirmative('list_outdated'):
            self.__run_npm_command('outdated', self.target)

        return FormulaBase.update(self)

    def activate(self):
        if self.source.is_affirmative('active_only', False):
            npm_root = self.target.get('npm_root')
            modules_dir = os.path.join(npm_root, 'node_modules')
            modules_restore = os.path.join(npm_root,
                                           'node_modules.{ns}'.format(
                                               ns=self.source.manifest.namespace))
            modules_bak = os.path.join(npm_root, 'node_modules.sv')

            if os.path.exists(modules_dir):
                if os.path.exists(modules_bak):
                    shutil.rmtree(modules_bak)
                shutil.move(modules_dir, modules_bak)
            shutil.move(modules_restore, modules_dir)
        FormulaBase.activate(self)

    def deactivate(self):
        if self.source.is_affirmative('active_only', False):
            npm_root = self.source.get('npm_root')
            modules_dir = os.path.join(npm_root, 'node_modules')
            modules_save = os.path.join(npm_root,
                                        'node_modules.{ns}'.format(
                                            ns=self.source.manifest.namespace))

            if os.path.exists(modules_save):
                shutil.rmtree(modules_save)
            shutil.move(modules_dir, modules_save)
        FormulaBase.deactivate(self)

    def __install_nvm_version(self, config=None):
        config = self.target if config is None else config
        version = config.get('node_version')
        self.__run_command('nvm install {version}'.format(version=version),
                           interactive=True, config=config)

    def __nvm_use(self, config=None):
        config = self.target if config is None else config
        if config.has('node_version'):
            return 'nvm use {version}'.format(version=config.get('node_version'))
        return ''

    def __run_npm_command(self, npm_command, config):
        root = config.get('npm_root')
        interactive = False
        # using depth 0, even though it's the default, to minimize npm's tree output

        command = "npm {cmd} --depth 0".format(cmd=npm_command)
        if config.has('node_version'):
            command = "{use} && {cmd}".format(
                use=self.__nvm_use(config=config),
                cmd=command)
            interactive = True
        self.__run_command(command, root=root, interactive=interactive, config=config)

    def __run_command(self, command, root=None, interactive=False, config=None):
        shell = interactive
        # using depth 0, even though it's the default, to minimize npm's tree output

        if interactive:
            command = "bash -i -c '{cmd}'".format(cmd=command).format(cmd=command)
            shell = True
        suppress_output = config.is_affirmative('redirect_stdout_to_log', 'true') if config is not None else True
        stdout = subprocess.PIPE if suppress_output else None
        return_code, output = lib.call(command, shell=shell, stdout=stdout, cwd=root)
        if config.is_affirmative('fail_on_error', True) and return_code != 0:
            raise NPMFormulaException("npm returned a return code of {0}!".format(return_code))
        return True
