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

    valid_options = FormulaBase.valid_options + ['source', 'target']
    # validated internally
    _required_options = ['source', 'target']
    deprecated_options = ['src', 'dest']
    deprecated_warnings = {
        'src': 'Option "src" in {feature} has been deprecated, use "source" instead',
        'dest': 'Option "dest" in {feature} has been deprecated, use "target" instead'
    }
    option_aliases = {
        'src': 'source',
        'dest': 'target'
    }

    def install(self):
        targetOpts = self.__get_options(self.target)
        self.__create_symlink(**targetOpts)
        FormulaBase.install(self)

    def update(self):
        sourceOpts = self.__get_options(self.source)
        targetOpts = self.__get_options(self.target)

        # compare old and new link source and link target
        if (sourceOpts['source'] != targetOpts['source'] or
            sourceOpts['target'] != targetOpts['target']):
            self.__remove_symlink(**sourceOpts)
            self.__create_symlink(**targetOpts)

        return FormulaBase.update(self)

    # internally validating required_options to accommodate deprecated options
    def validate(self):
        if self.target:
            targetOpts = self.__get_options(self.target)
            for k in self._required_options:
                if k not in targetOpts:
                    self._log_error("Required option %s not present in feature %s!" % (k, self.feature_name))
        return FormulaBase.validate(self)

    def remove(self):
        sourceOpts = self.__get_options(self.source)
        self.__remove_symlink(**sourceOpts)
        FormulaBase.remove(self)

    def activate(self):
        sourceOpts = self.__get_options(self.source)
        self.__create_symlink(**sourceOpts)
        FormulaBase.activate(self)

    def deactivate(self):
        sourceOpts = self.__get_options(self.source)
        if config.is_affirmative('active_only', 'true'):
            self.__remove_symlink(**sourceOpts)
        FormulaBase.deactivate(self)

    def __get_options(self, config):
        if config.has('source'):
            return { 'source': config.get('source'), 'target': config.get('target') }
        else:
            return { 'source': config.get('src'), 'target': config.get('dest') }

    def __create_symlink(self, source, target):
        link_source = os.path.expanduser(source)
        link_target = os.path.expanduser(target)
        parts = link_target.split('/')
        target_name = parts.pop()
        target_dir = '/'.join(parts)

        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)
        if os.path.islink(link_source):
            os.unlink(link_source)

        self.logger.debug("Creating symbolic link {0} > {1}".format(link_source, link_target))
        os.symlink(link_target, link_source)
        return True

    def __remove_symlink(self, source, target):
        link_source = os.path.expanduser(source)
        link_target = os.path.expanduser(target)

        if os.path.islink(link_source):
            self.logger.debug("Removing symbolic link {0} > {1}".format(link_source, link_target))
            if os.path.islink(link_source):
                os.unlink(link_source)
        return True
