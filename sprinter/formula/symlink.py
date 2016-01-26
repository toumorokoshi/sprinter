"""
Creates a symbolic link. If active_only is True, then it is
removed when the environment is deactivated.

[symlink]
formula = sprinter.formula.symlink
src=/path/to/src
dest=/path/to/dest
active_only=True
"""
from __future__ import unicode_literals
from sprinter.formula.base import FormulaBase
from sprinter.exceptions import FormulaException

import os

class SymlinkFormulaException(FormulaException):
    pass


class SymlinkFormula(FormulaBase):

    valid_options = FormulaBase.valid_options + ['src',
                                                 'dest']

    def install(self):
        self.__create_symlink('target')
        FormulaBase.install(self)

    def update(self):
        value = self.__remove_symlink('target')
        value = self.__create_symlink('target')
        return value or FormulaBase.update(self)

    def remove(self):
        value = self.__create_symlink('source')
        FormulaBase.remove(self)

    def activate(self):
        self.__create_symlink('source')
        FormulaBase.activate(self)

    def deactivate(self):
        config = getattr(self, 'source')
        if config.has('active_only') and config.is_affirmative('active_only'):
            self.__remove_symlink('source')
        FormulaBase.deactivate(self)

    def __create_symlink(self, manifest_type):
        config = getattr(self, manifest_type)
        if config.has('src') and config.has('dest'):
            src = os.path.expanduser(config.get('src'))
            dest = os.path.expanduser(config.get('dest'))
            parts = dest.split('/')
            dest_name = parts.pop()
            dest_dir = '/'.join(parts)

            if not os.path.isdir(dest_dir):
                os.mkdir(dest_dir)
            if os.path.islink(dest):
                os.unlink(dest)

            self.logger.debug("Creating symbolic link {0} > {1}".format(dest, src))
            os.symlink(src, dest)
            return True

    def __remove_symlink(self, manifest_type):
        config = getattr(self, manifest_type)
        if config.has('src') and config.has('dest'):
            src = os.path.expanduser(config.get('src'))
            dest = os.path.expanduser(config.get('dest'))

            if os.path.islink(dest):
                self.logger.debug("Removing symbolic link {0} > {1}".format(dest, src))
                self.directory.remove_feature(self.feature_name)
            return True
