"""
Unpacks and deploys to a location

[unpack]
formula = sprinter.formulas.unpack
symlink = bin/go
remove_common_prefix = true
url = https://go.googlecode.com/files/go1.1.linux-amd64.tar.gz
strip-top-level-directory=True
"""

import os
import shutil

from sprinter.formulabase import FormulaBase


class UnpackFormula(FormulaBase):
    """ A sprinter formula for unpacking a compressed package and extracting it"""

    def install(self, feature_name, config):
        self.__install(feature_name, config)
        if 'executable' in config:
            symlink_target = config['symlink'] if 'symlink' in config else config['executable']
            self.__symlink_executable(feature_name, config['executable'], symlink_target)
        super(UnpackFormula, self).setup(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        if (source_config['formula'] != target_config['formula']
           or source_config['url'] != target_config['url']):
            shutil.rmtree(self.directory.install_directory(feature_name))
            self.__install(target_config['url'], self.directory.install_directory(feature_name))
            if 'command' in target_config:
                self.logger.info(self.lib.call(target_config['command'],
                                               bash=True,
                                               cwd=self.directory.install_directory(feature_name)))
        if 'rc' in target_config:
            self.directory.add_to_rc(target_config['rc'])

    def remove(self, feature_name, config):
        super(UnpackFormula, self).destroy(feature_name, config)

    def __install(self, feature_name, config):
        remove_common_prefix = 'remove_common_prefix' in config and \
                               config['remove_common_prefix'].lower().startswith('t')
        if config['type'] == "tar.gz":
            self.lib.extract_targz(config['url'], self.directory.install_directory(feature_name),
                                   remove_common_prefix=remove_common_prefix)
        elif config['type'] == "zip":
            self.lib.extract_zip(config['url'], self.directory.install_directory(feature_name),
                                 remove_common_prefix=remove_common_prefix)
        elif config['type'] == "dmg":
            if not self.system.isOSX():
                self.logger.warn("Non OSX based distributions can not install a dmg!")
            else:
                self.lib.extract_dmg(config['url'], self.directory.install_directory(feature_name),
                                     remove_common_prefix=remove_common_prefix)

    def __symlink_executable(self, feature_name, source, target):
        source_path = os.path.join(self.directory.install_directory(feature_name), source)
        self.logger.debug("Symlinking executable at %s to bin/%s" %
                          (source_path, target))
        self.directory.symlink_to_bin(target, source_path)
