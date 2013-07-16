"""
Formula base is an abstract base class outlining the method required
and some documentation on what they should provide.
"""
import logging
import os

from sprinter.core import LOGGER, PHASES
from sprinter.exceptions import FormulaException


class FormulaBase(object):

    def __init__(self, environment, source, target, logger=LOGGER):
        self.environment = environment
        self.directory = environment.directory
        self.config = environment.config
        self.injections = environment.injections
        self.system = environment.system
        self.lib = environment.lib
        self.logger = LOGGER
        self.source = source
        self.target = target
        if not (source or target):
            raise FormulaException("A formula requires a source and/or a target!")

    def install(self, feature_name, config):
        """ Install is called when a feature does not previously exist. """
        install_directory = self.directory.install_directory(feature_name)
        cwd = install_directory if os.path.exists(install_directory) else None
        if config.has('rc'):
            self.directory.add_to_rc(config.get('rc'))
        if 'command' in config:
            self.lib.call(config['command'],
                          shell=True,
                          cwd=cwd)

    def update(self, feature_name, source_config, target_config):
        """ Update is called when a feature previously exists. """
        install_directory = self.directory.install_directory(feature_name)
        cwd = install_directory if os.path.exists(install_directory) else None
        if 'rc' in target_config:
            self.directory.add_to_rc(target_config['rc'])
        if 'command' in target_config:
            self.lib.call(target_config['command'],
                          shell=True,
                          cwd=cwd)

    def remove(self, feature_name, config):
        """ Remove is called when a feature no longer exists. """

    def deactivate(self, feature_name, config):
        """ Deactivate is called when a user deactivates the environment. """

    def activate(self, feature_name, config):
        """ Activate is called when a user activates the environment. """

    def validate(self, config):
        """
        validates the feature configuration, and returns a list of errors (empty list if no error)
        """
        return []

    # these methods are overwritten less often, and are not recommended to do so.
    def sync_phase(self):
        """ Says whether a sync is an install, update, or delete """
        if not self.target:
            return PHASES.INSTALL
        if not self.source:
            

    def sync(self):
        """ Updates the state of the feature to what it should be """

    def resolve(source_config, target_config):
        """ Resolve differences between the target and the source configuration """
        for k in (k for k in source_config.keys() if not target_config.has(k)):
            target_config.set(k, source_config.get(k))

