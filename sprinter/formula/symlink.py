"""
Creates a symbolic link. If active_only is True, then it is
removed when the environment is deactivated.

[symlink]
formula = sprinter.formula.symlink
source=/path/to/source
target=/path/to/target
active_only=True
"""
from __future__ import unicode_literals
from sprinter.formula.base import FormulaBase
from sprinter.exceptions import FormulaException

import os

class SymlinkFormulaException(FormulaException):
    pass


class SymlinkFormula(FormulaBase):

    valid_options = FormulaBase.valid_options + ['source',
                                                 'target']

    def install(self):
        self.__create_symlink('target')
        FormulaBase.install(self)

    def update(self):
        source = getattr(self, 'source')
        target = getattr(self, 'target')
        # compare old and new link source and link target
        if (source.get('source') != target.get('source')
            or source.get('target') != target.get('target')):
            self.__remove_symlink('target')
            self.__create_symlink('target')

        return FormulaBase.update(self)

    def remove(self):
        self.__create_symlink('source')
        FormulaBase.remove(self)

    def activate(self):
        self.__create_symlink('source')
        FormulaBase.activate(self)

    def deactivate(self):
        config = getattr(self, 'source')
        if config.is_affirmative('active_only', 'true'):
            self.__remove_symlink('source')
        FormulaBase.deactivate(self)

    def __create_symlink(self, manifest_type):
        config = getattr(self, manifest_type)
        if config.has('source') and config.has('target'):
            link_source = os.path.expanduser(config.get('source'))
            link_target = os.path.expanduser(config.get('target'))
            parts = link_target.split('/')
            target_name = parts.pop()
            target_dir = '/'.join(parts)

            if not os.path.isdir(target_dir):
                os.mkdir(target_dir)
            if os.path.islink(link_target):
                os.unlink(link_target)

            self.logger.debug("Creating symbolic link {0} > {1}".format(link_target, link_source))
            os.symlink(link_source, link_target)
            return True

    def __remove_symlink(self, manifest_type):
        config = getattr(self, manifest_type)
        if config.has('source') and config.has('target'):
            link_source = os.path.expanduser(config.get('source'))
            link_target = os.path.expanduser(config.get('target'))

            if os.path.islink(link_target):
                self.logger.debug("Removing symbolic link {0} > {1}".format(link_target, link_source))
                self.directory.remove_feature(self.feature_name)
            return True
