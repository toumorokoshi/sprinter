"""
Unpacks and deploys to a location

[unpack]
formula = sprinter.formula.unpack
executable = bin/go
symlink = go
remove_common_prefix = true
url = https://go.googlecode.com/files/go1.1.linux-amd64.tar.gz
target = /tmp/
"""

from __future__ import unicode_literals
import os

from sprinter.formula.base import FormulaBase
from sprinter.lib import ExtractException, system
from sprinter.exceptions import FormulaException
from sprinter.core.directory import DirectoryException
import sprinter.lib as lib


class UnpackFormulaException(FormulaException):
    """ Covers execptions with the unpack formula """


class UnpackFormula(FormulaBase):
    """ A sprinter formula for unpacking a compressed package and extracting it"""

    valid_options = FormulaBase.valid_options + ['executable', 'symlink', 'target',
                                                 'remove_common_prefix', 'type']
    required_options = FormulaBase.required_options + ['url']

    def install(self):
        self.__install(self.target)
        if self.target.has('executable'):
            symlink_target = self.target.get('symlink',
                                             self.target.get('executable'))
            self.__symlink_executable(self.target.get('executable'),
                                      symlink_target)
        FormulaBase.install(self)

    def update(self):
        acted = False
        if not os.path.exists(self._get_destination()):
            self.install()
            return True

        if self.source.get('url') != self.target.get('url'):
            acted = True
            if os.path.exists(self.directory.install_directory(self.feature_name)):
                try:
                    self.directory.remove_feature(self.feature_name)
                except DirectoryException:
                    self.logger.exception()
                    self.logger.error("Unable to remove old directory!")
            self.__install(self.target)
        if self.source.has('executable'):
            symlink = self.source.get('symlink', self.source.get('executable'))
            if os.path.exists(symlink) and os.path.islink(symlink):
                try:
                    self.directory.remove_from_bin(
                        self.source('symlink', self.source.get('executable')))
                    acted = True
                except DirectoryException:
                    pass
        if self.target.has('executable'):
            symlink = self.target.get('symlink', self.target.get('executable'))
            if not os.path.exists(symlink):
                acted = True
                self.__symlink_executable(self.target.get('executable'),
                                          symlink)
        FormulaBase.update(self)
        return acted

    def remove(self):
        if self.source.has('executable'):
            symlink = self.source.get('symlink', self.source.get('executable'))
            if os.path.exists(symlink) and os.path.islink(symlink):
                try:
                    self.directory.remove_from_bin(
                        self.source('symlink', self.source.get('executable')))
                except DirectoryException:
                    pass
        FormulaBase.remove(self)

    def __install(self, config):
        remove_common_prefix = (config.has('remove_common_prefix') and
                                config.is_affirmative('remove_common_prefix'))
        url_type = config.get('type', config.get('url'))
        try:
            if url_type.endswith("tar.gz") or url_type.endswith("tar.bz2") or url_type.endswith("tar"):
                lib.extract_targz(config.get('url'), self._get_destination(),
                                  remove_common_prefix=remove_common_prefix)

            elif config.get('type', config.get('url')).endswith("zip"):
                lib.extract_zip(config.get('url'), self._get_destination(),
                                remove_common_prefix=remove_common_prefix)

            elif config.get('type', config.get('url')).endswith("dmg"):
                if not system.is_osx():
                    self.logger.warn("Non OSX based distributions can not install a dmg!")
                else:
                    lib.extract_dmg(config.get('url'), self._get_destination(),
                                    remove_common_prefix=remove_common_prefix)
        except ExtractException:
            self.logger.warn("Unable to extract file for feature %s" % self.feature_name)

    def __symlink_executable(self, source, target):
        source_path = os.path.join(self.directory.install_directory(self.feature_name),
                                   source)
        self.logger.debug("Symlinking executable at %s to bin/%s" %
                          (source_path, target))
        try:
            self.directory.symlink_to_bin(target, source_path)
        except OSError:
            self.logger.warn("Could not find source path, unable to symlink! %s" % source)

    def _get_destination(self):
        return self.target.get(
            'target', self.directory.install_directory(self.feature_name)
        )
