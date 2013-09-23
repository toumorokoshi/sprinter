"""
Unpacks and deploys to a location

[unpack]
formula = sprinter.formulas.unpack
executable = bin/go
symlink = go
remove_common_prefix = true
url = https://go.googlecode.com/files/go1.1.linux-amd64.tar.gz
target = /tmp/
"""

import os

from sprinter.formulabase import FormulaBase
from sprinter.exceptions import ExtractException
from sprinter.directory import DirectoryException
import sprinter.lib as lib


class UnpackFormulaException(Exception):
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
        if self.source.get('url') != self.target.get('url'):
            if os.path.exists(self.directory.install_directory(self.feature_name)):
                try:
                    self.directory.remove_feature(self.feature_name)
                except DirectoryException:
                    self.logger.error("Unable to remove old directory!")
            self.__install(self.target)
        if self.source.has('executable'):
            symlink = self.source.get('symlink', self.source.get('executable'))
            if os.path.exists(symlink) and os.path.islink(symlink):
                try:
                    self.directory.remove_from_bin(
                        self.source('symlink', self.source.get('executable')))
                except DirectoryException:
                    pass
        if self.target.has('executable'):
            symlink = self.target.get('symlink', self.target.get('executable'))
            if not os.path.exists(symlink):
                self.__symlink_executable(self.target.get('executable'),
                                          symlink)
        FormulaBase.update(self)

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
        destination = config.get('target', self.directory.install_directory(self.feature_name))
        try:
            if config.get('type', config.get('url')).endswith("tar.gz"):
                lib.extract_targz(config.get('url'), destination,
                                  remove_common_prefix=remove_common_prefix)

            elif config.get('type', config.get('url')).endswith("zip"):
                lib.extract_zip(config.get('url'), destination,
                                remove_common_prefix=remove_common_prefix)

            elif config.get('type', config.get('url')).endswith("dmg"):
                if not self.system.isOSX():
                    self.logger.warn("Non OSX based distributions can not install a dmg!")
                else:
                    lib.extract_dmg(config.get('url'), destination,
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
