"""
A module that completely encapsulates a class. This should be a
complete object representing any data needed by recipes.
"""

import platform
from sprinter.manifest import Manifest
from sprinter.directory import Directory


class Environment(object):

    def __init__(self, target_manifest, source_manifest=None, namespace=None):
        self.namespace = namespace
        self.manifest = Manifest(target_manifest, source_manifest=source_manifest)
        self.directory = Directory(namespace=namespace)
        self.environment = self.__initialize_environment()

    def __initialize_environment(self):
        """
        Return an environment dict with various information about the
        environment

        e.g.
        """
        environment_dict = {}
        (system, node, release, version, machine, processor) = platform.uname()
        environment_dict['system'] = system
        environment_dict['node'] = node
        environment_dict['processor'] = processor
        return environment_dict

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
        return self.directory.rc_path()
