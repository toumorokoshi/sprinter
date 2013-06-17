"""
Unpacks and deploys to a location

[unpack]
formula = sprinter.formulas.unpack
executable = bin/go
symlink = go
remove_common_prefix = true
url = https://go.googlecode.com/files/go1.1.linux-amd64.tar.gz
target = /tmp/
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
        super(UnpackFormula, self).install(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        if (source_config['formula'] != target_config['formula']
           or source_config['url'] != target_config['url']):
            if os.path.exists(self.directory.install_directory(feature_name)):
                shutil.rmtree(self.directory.install_directory(feature_name))
            self.__install(feature_name, target_config)
            if 'command' in target_config:
                self.logger.info(self.lib.call(target_config['command'],
                                               bash=True,
                                               cwd=self.directory.install_directory(feature_name)))
        if 'executable' in source_config:
            symlink = source_config['symlink'] if 'symlink' in source_config else source_config['executable']
            if os.path.exists(symlink) and os.path.islink(symlink):
                try:
                    self.directory.remove_from_bin(source_config['symlink'] if 'symlink' in source_config
                                                   else source_config['executable'])
                except OSError:
                    pass
        if 'executable' in target_config:
            symlink_target = target_config['symlink'] if 'symlink' in target_config else target_config['executable']
            if not os.path.exists(symlink_target):
                self.__symlink_executable(feature_name, target_config['executable'], symlink_target)
        if 'rc' in target_config:
            self.directory.add_to_rc(target_config['rc'])

    def remove(self, feature_name, config):
        super(UnpackFormula, self).remove(feature_name, config)

    def __install(self, feature_name, config):
        remove_common_prefix = 'remove_common_prefix' in config and \
                               config['remove_common_prefix'].lower().startswith('t')
        destination = (self.directory.install_directory(feature_name) if 'target'
                       not in config else config['target'])
        if config['type'] == "tar.gz":
            self.lib.extract_targz(config['url'], destination,
                                   remove_common_prefix=remove_common_prefix)
        elif config['type'] == "zip":
            self.lib.extract_zip(config['url'], destination,
                                 remove_common_prefix=remove_common_prefix)
        elif config['type'] == "dmg":
            if not self.system.isOSX():
                self.logger.warn("Non OSX based distributions can not install a dmg!")
            else:
                self.lib.extract_dmg(config['url'], destination,
                                     remove_common_prefix=remove_common_prefix)

    def __symlink_executable(self, feature_name, source, target):
        source_path = os.path.join(self.directory.install_directory(feature_name), source)
        self.logger.debug("Symlinking executable at %s to bin/%s" %
                          (source_path, target))
        try:
            self.directory.symlink_to_bin(target, source_path)
        except OSError:
            self.logger.warn("Could not find source path, unable to symlink! %s" % source)
