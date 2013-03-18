"""
A module that completely encapsulates a sprinter environment. This should be a
complete object representing any data needed by recipes.
"""

import logging
import re
import sys
from sprinter.manifest import Config, Manifest
from sprinter.directory import Directory
from sprinter.injections import Injections
from sprinter.system import System
from sprinter.lib import get_recipe_class

config_substitute_match = re.compile("%\(config:([^\)]+)\)")


class Environment(object):

    recipe_dict = {}
    config = None  # handles the configuration, and manifests
    system = None  # stores system information
    injections = None  # handles injections
    directory = None  # handles interactions with the environment directory

    def __init__(self, logger=None, logging_level=logging.INFO):
        self.system = System()
        self.logger = self.__build_logger(logger=logger, level=logging_level)

    def install(self, raw_target_manifest, namespace=None):
        """
        Install an environment based on the target manifest passed
        """
        target_manifest = Manifest(raw_target_manifest, namespace=namespace)
        directory = Directory(target_manifest.namespace)
        if not directory.new:
            self.logger.info("Namespace %s already exists, updating..." % \
                             target_manifest.namespace)
            self._update(Manifest(directory.manifest_path),
                         target_manifest,
                         directory=directory)
        else:
            self.logger.info("Installing environment %s..." % target_manifest.namespace)
            self._install(target_manifest)

    def update(self, namespace):
        """
        Update a namespace
        """
        directory = Directory(namespace)
        if directory.new:
            self.logger.error("Namespace %s is not yet installed!" % namespace)
            return
        source_manifest = Manifest(directory.manifest_path)
        source = source_manifest.source()
        if not source:
            self.logger.error("Installed manifest for %s has no source!" % namespace)
            return
        target_manifest = Manifest(source, namespace=namespace)
        self.logger.info("Updating environment %s..." % target_manifest.namespace)
        self._update(source_manifest, target_manifest)

    def remove(self, namespace):
        """
        Remove an environment namespace
        """
        directory = Directory(namespace)
        if directory.new:
            self.logger.error("Namespace %s does not exist!" % namespace)
            return
        source_manifest = Manifest(directory.manifest_path)
        self.logger.info("Removing environment %s..." % source_manifest.namespace)
        self._remove(source_manifest, directory=directory)

    def deactivate(self, namespace):
        """
        Deactivate an environment namespace
        """
        directory = Directory(namespace, rewrite_rc=False)
        if directory.new:
            self.logger.error("Namespace %s does not exist!" % namespace)
            return
        source_manifest = Manifest(directory.manifest_path)
        self.logger.info("Deactivating environment %s..." % source_manifest.namespace)
        self._deactivate(source_manifest, directory=directory)

    def activate(self, namespace):
        """
        Activate an environment namespace
        """
        directory = Directory(namespace, rewrite_rc=False)
        if directory.new:
            self.logger.error("Namespace %s does not exist!" % namespace)
            return
        source_manifest = Manifest(directory.manifest_path)
        self.logger.info("Activating environment %s..." % source_manifest.namespace)
        self._activate(source_manifest, directory=directory)

    def reload(self, namespace):
        """
        Activate an environment namespace
        """
        directory = Directory(namespace, rewrite_rc=False)
        if directory.new:
            self.logger.error("Namespace %s does not exist!" % namespace)
            return
        source_manifest = Manifest(directory.manifest_path)
        self.logger.info("Reloading environment %s..." % source_manifest.namespace)
        self._reload(source_manifest, directory=directory)

    def initialize(self, source_manifest=None, target_manifest=None, directory=None):
        """
        Initialize the environment for a sprinter action
        """
        self.config = Config(source=source_manifest, target=target_manifest)
        self.directory = directory if directory else Directory(self.config.namespace)
        self.directory.initialize()
        self.injections = Injections(wrapper="SPRINTER_%s" % self.config.namespace)
        self.config.grab_inputs()

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

    def _install(self, target_manifest, directory=None):
        """
        Intall an environment from a target manifest Manifest
        """
        self.initialize(target_manifest=target_manifest, directory=directory)
        self._run_setups()
        self.injections.inject("~/.bash_profile", "[ -d %s ] && . %s/.rc" %
                (self.directory.root_dir, self.directory.root_dir))
        self.finalize()

    def _update(self, source_manifest, target_manifest, directory=None):
        """
        Intall an environment from a target manifest Manifest
        """
        self.initialize(target_manifest=target_manifest, directory=directory)
        self._run_setups()
        self._run_updates()
        self._run_destroys()
        self.finalize()

    def _remove(self, source_manifest, directory=None):
        """
        Remove an environment defined by a source_manifest
        """
        self.initialize(source_manifest=source_manifest)
        self._run_destroys()
        self.injections.clear("~/.bash_profile")
        self.finalize()

    def _deactivate(self, source_manifest, directory=None):
        """
        Remove an environment defined by a source_manifest
        """
        self.initialize(source_manifest=source_manifest)
        self._run_deactivates()
        self.injections.clear("~/.bash_profile")
        self.finalize()

    def _activate(self, source_manifest, directory=None):
        """
        Remove an environment defined by a source_manifest
        """
        self.initialize(source_manifest=source_manifest)
        self._run_activates()
        self.injections.inject("~/.bash_profile", "[ -d %s ] && . %s/.rc" %
                (self.directory.root_dir, self.directory.root_dir))
        self.finalize()

    def _run_setups(self):
        for name, config in self.config.setups().items():
            self.logger.info("Setting up %s..." % name)
            recipe_instance = self.__get_recipe_instance(config['target']['recipe'])
            recipe_instance.setup(name, config['target'])

    def _run_updates(self):
        for name, config in self.config.updates().items():
            self.logger.info("Updating %s..." % name)
            recipe_instance = self.__get_recipe_instance(config['target']['recipe'])
            recipe_instance.update(name, config)

    def _run_destroys(self):
        for name, config in self.config.destroys().items():
            self.logger.info("Removing %s..." % name)
            recipe_instance = self.__get_recipe_instance(config['source']['recipe'])
            recipe_instance.update(name, config)

    def _run_activates(self):
        for name, config in self.config.activations().items():
            self.logger.info("Activating %s..." % name)
            recipe_instance = self.__get_recipe_instance(config['source']['recipe'])
            recipe_instance.update(name, config)

    def _run_deactivates(self):
        for name, config in self.config.deactivations().items():
            self.logger.info("Deactivating %s..." % name)
            recipe_instance = self.__get_recipe_instance(config['source']['recipe'])
            recipe_instance.update(name, config)

    def _run_reloads(self):
        for name, config in self.config.reloads().items():
            self.logger.info("Reloading %s..." % name)
            recipe_instance = self.__get_recipe_instance(config['source']['recipe'], self)
            recipe_instance.update(name, config)

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

    def __get_recipe_instance(self, recipe):
        """
        get an instance of the recipe object object if it exists, else
        create one, add it to the dict, and pass return it.
        """
        if recipe not in self.recipe_dict:
            self.recipe_dict[recipe] = get_recipe_class(recipe, self)
        return self.recipe_dict[recipe]
