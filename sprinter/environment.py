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
from sprinter.lib import get_recipe_class

debian_match = re.compile(".*(ubuntu|debian).*", re.IGNORECASE)
fedora_match = re.compile(".*(RHEL).*", re.IGNORECASE)

config_substitute_match = re.compile("%\(config:([^\)]+)\)")


class Environment(object):

    recipe_dict = {}

    def __init__(self, namespace=None, logger=None, logging_level=logging.INFO,
            rewrite_rc=True):
        self.namespace = namespace
        (system, node, release, version, machine, processor) = platform.uname()
        self.system = system
        self.node = node
        self.processor = processor
        self.logger = self.__build_logger(logger=logger, level=logging_level)
        self.rewrite_rc = rewrite_rc

    def load_manifest(self, target_manifest, source_manifest=None):
        self.manifest = Manifest(target_manifest,
                                 source_manifest=source_manifest,
                                 namespace=self.namespace)
        self.namespace = self.manifest.namespace
        self.directory = Directory(namespace=self.namespace)
        if not source_manifest:
            self.manifest.load_source(self.directory.config_path())
        self.injections = Injections(wrapper="SPRINTER_%s" % self.namespace)
        self.grab_inputs()

    def load_namespace(self, namespace=None):
        if namespace:
            self.namespace = namespace
        self.directory = Directory(namespace=self.namespace)
        self.manifest = Manifest(source_manifest=self.directory.config_path(),
                                 target_manifest=self.directory.config_path(),
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
        self.add_to_rc("export PATH=%s:$PATH" % self.directory.bin_path())
        self.injections.commit()

    def context(self):
        """ get a context dictionary to replace content """
        context_dict = self.manifest.get_context_dict()
        for s in self.manifest.target_sections():
            context_dict["%s:root_dir" % s] = self.directory.install_directory(s)
        # add environment information
        context_dict['config:node'] = self.node
        return context_dict

    def validate_context(self, content):
        """ check if all the config variables desired exist, and prompt them if not """
        values = config_substitute_match.findall(content)
        for v in values:
            if v not in self.manifest.config:
                self.get_config(v, default=None, temporary=False)

    def deactivate(self):
        """ deactivate environments """
        for name, config in self.manifest.deactivations().items():
            self.logger.info("Deactivating %s..." % name)
            recipe_instance = self.__get_recipe_instance(config['source']['recipe'])
            recipe_instance.deactivate(name, config['source'])
        self.injections.clear("~/.bash_profile")

    def activate(self):
        """ activate environment specific injections """
        for name, config in self.manifest.activations().items():
            self.logger.info("Activating %s..." % name)
            recipe_instance = self.__get_recipe_instance(config['source']['recipe'])
            recipe_instance.activate(name, config['source'])
        self.injections.inject("~/.bash_profile", "[ -d %s ] && . %s/.rc" % 
                (self.directory.root_dir, self.directory.root_dir))

    def __get_recipe_instance(self, recipe):
        """
        get an instance of the recipe object object if it exists, else
        create one, add it to the dict, and pass return it.
        """
        if recipe not in self.recipe_dict:
            self.recipe_dict[recipe] = get_recipe_class(recipe, self)
        return self.recipe_dict[recipe]

    # wrapper for injections methods
    def inject(self, filename, content):
        return self.injections.inject(filename, content)

    def clear(self, filename):
        return self.injections.clear(filename)

    def commit_injections(self, filename, content):
        return self.injections.commit()

    # wrapper for manifest methods
    def grab_inputs(self):
        return self.manifest.grab_inputs()

    def get_config(self, param_name, default=None, temporary=False):
        return self.manifest.get_config(param_name, default, temporary)

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
        self.validate_context(content)
        self.logger.debug("adding %s to rc" % content)
        return self.directory.add_to_rc(content % self.context())

    def rc_path(self):
        return self.directory.rc_path
