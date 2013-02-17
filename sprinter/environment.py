"""
A module that completely encapsulates a class. This should be a
complete object representing any data needed by recipes.
"""

import logging
import platform
import re
import sys
from sprinter.manifest import Manifest
from sprinter.directory import Directory

debian_match = re.compile(".*(Ubuntu|Debian).*")
fedora_match = re.compile(".*(RHEL).*")


class Environment(object):

    def __init__(self, target_manifest, source_manifest=None, namespace=None, logger=None, logging_level=logging.INFO):
        self.namespace = namespace
        self.manifest = Manifest(target_manifest, source_manifest=source_manifest)
        self.directory = Directory(namespace=namespace)
        (system, node, release, version, machine, processor) = platform.uname()
        self.system = system
        self.node = node
        self.processor = processor
        self.logger = self.__build_logger(logger=logger, level=logging_level)

    def __build_logger(self, logger=None, level=logging.INFO):
        """ return a logger. if logger is none, generate a logger from stdout """
        if not logger:
            logger = logging.getLogger('sprinter')
            out_hdlr = logging.StreamHandler(sys.stdout)
            out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            out_hdlr.setLevel(level)
            logger.addHandler(out_hdlr)
        logger.setLevel(level)
        return logger

    def isOSX(self):
        return self.system == "darwin"

    def isLinux(self):
        return self.system == "Linux"

    def isDebianBased(self):
        return debian_match.match(self.node) is not None

    def isFedoraBased(self):
        return fedora_match.match(self.node) is not None

    # wrapper for manifest methods
    def setups(self):
        return self.manifest.setups()

    def updates(self):
        return self.manifest.updates()

    def destroys(self):
        return self.manifest.destroys()

    def validate(self):
        return self.manifest.validate()

    # these methods wrap directory methods
    def symlink_to_bin(self, name, path):
        return self.directory.symlink_to_bin(name, path)

    def symlink_to_lib(self, name, path):
        return self.directory.symlink_to_lib(name, path)

    def install_directory(self, feature_name):
        return self.directory.install_directory(feature_name)

    def add_to_rc(self, content):
        return self.directory.add_to_rc(content)

    def rc_path(self):
        return self.directory.rc_path
