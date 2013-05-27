"""
Unpacks and deploys to a location
"""

import gzip
import os
import tarfile
import urllib
from StringIO import StringIO

from sprinter.formulastandard import FormulaStandard
from sprinter.lib import extract_dmg, extract_targz


class UnpackFormula(FormulaStandard):
    """ A sprinter formula for unpacking a compressed package and extracting it"""

    def setup(self, feature_name, config):
        self.__install(feature_name, config)
        if 'executable' in config:
            symlink_target = config['symlink'] if 'symlink' in config else config['executable']
            self.__symlink_executable(feature_name, config['executable'], symlink_target)
        super(UnpackFormula, self).setup(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        if (source_config['formula'] != target_config['formula']
            or source_config['url'] != target_config['url']):
            shutil.rmtree(self.directory.install_directory(feature_name))
            self.__install(config['url'], self.directory.install_directory(feature_name))
        super(UnpackFormula, self).update(feature_name, source_config, target_config)

    def destroy(self, feature_name, config):
        super(UnpackFormula, self).destroy(feature_name, config)

    def __install(self, feature_name, config):
        if config['type'] == "tar.gz":
            extract_targz(config['url'], self.directory.install_directory(feature_name))
        else if config['type'] == "dmg":
            extract_dmg(config['url'], self.directory.install_directory(feature_name))

    def __extract_targz(self, url, target_dir):
        """ extract a targz and install to the target directory """
        self.environment.logger.debug("Extracting package at %s" % url)
        gz = gzip.GzipFile(fileobj=StringIO(urllib.urlopen(url).read()))
        tf = tarfile.TarFile(fileobj=gz)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        tf.extractall(path=target_dir)

    def __symlink_executable(self, feature_name, source, target):
        source_path = os.path.join(self.directory.install_directory(feature_name), source)
        self.logger.debug("Symlinking executable at %s to bin/%s" %
                          (source_path, target))
        self.directory.symlink_to_bin(target, source_path)
