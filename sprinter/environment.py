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
from sprinter.injections import Injections

debian_match = re.compile(".*(Ubuntu|Debian).*")
fedora_match = re.compile(".*(RHEL).*")


class Environment(object):

    def __init__(self, namespace=None, logger=None, logging_level=logging.INFO):
        self.namespace = namespace
        (system, node, release, version, machine, processor) = platform.uname()
        self.system = system
        self.node = node
        self.processor = processor
        self.logger = self.__build_logger(logger=logger, level=logging_level)

    def load_manifest(self, target_manifest, source_manifest=None):
        self.manifest = Manifest(target_manifest,
                                 source_manifest=source_manifest,
                                 namespace=self.namespace)
        self.namespace = self.manifest.namespace
        self.directory = Directory(namespace=self.namespace)
        if not source_manifest:
            self.manifest.load_source(self.directory.config_path())
        self.injections = Injections(wrapper="SPRINTER_%s" % self.namespace)

    def load_namespace(self, namespace=None):
        if namespace:
            self.namespace = namespace
        self.directory = Directory(namespace=self.namespace)
        self.manifest = Manifest(source_manifest=self.directory.config_path(),
                                 namespace=self.namespace)
        self.injections = Injections(wrapper="SPRINTER_%s" % self.namespace)

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

    def finalize(self):
        """ command to run at the end of sprinter's run """
        self.manifest.write(open(self.directory.config_path(), "w+"))
        self.injections.commit()

    def context(self):
        """ get a context dictionary to replace content """
        context_dict = self.manifest.get_context_dict()
        for s in self.manifest.target_sections():
            context_dict["%s:root_dir" % s] = self.directory.install_directory(s)
        return context_dict

    # wrapper for injections methods
    def inject(self, filename, content):
        return self.injections.inject(filename, content)

    def clear(self, filename):
        return self.injections.clear(filename)

    def commit_injections(self, filename, content):
        return self.injections.commit()

    # wrapper for manifest methods
    def load_target_implicit(self):
        return self.manifest.load_target_implicit()

    def setups(self):
        return self.manifest.setups()

    def updates(self):
        return self.manifest.updates()

    def destroys(self):
        return self.manifest.destroys()

    def reloads(self):
        return self.manifest.reloads()

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
        return self.directory.add_to_rc(content % self.context())

    def rc_path(self):
        return self.directory.rc_path
