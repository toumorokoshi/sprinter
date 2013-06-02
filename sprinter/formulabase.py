"""
Formula base is an abstract base class outlining the method required
and some documentation on what they should provide.
"""
import logging
import os


class FormulaBase(object):

    def __init__(self, environment):
        self.environment = environment
        self.directory = environment.directory
        self.config = environment.config
        self.injections = environment.injections
        self.system = environment.system
        self.lib = environment.lib
        self.logger = logging.getLogger('sprinter')

    def install(self, feature_name, config):
        """ Install is called when a feature does not previously exist. """
        install_directory = self.directory.install_directory(feature_name)
        cwd = install_directory if os.path.exists(install_directory) else None
        if 'rc' in config:
            self.directory.add_to_rc(config['rc'])
        if 'command' in config:
            self.logger.info(self.lib.call(config['command'],
                                           bash=True,
                                           cwd=cwd))

    def update(self, feature_name, source_config, target_config):
        """ Update is called when a feature previously exists. """
        install_directory = self.directory.install_directory(feature_name)
        cwd = install_directory if os.path.exists(install_directory) else None
        if 'rc' in target_config:
            self.directory.add_to_rc(target_config['rc'])
        if 'command' in target_config:
            self.logger.info(self.lib.call(target_config['command'],
                                           bash=True,
                                           cwd=cwd))

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
