"""
Recipe base is an abstract base class outlining the method required
and some documentation on what they should provide.
"""
import logging

from sprinter import lib
from sprinter.recipebase import RecipeBase


class RecipeStandard(RecipeBase):

    def __init__(self, environment):
        self.environment = environment
        self.directory = environment.directory
        self.config = environment.config
        self.injections = environment.injections
        self.system = environment.system
        self.logger = logging.getLogger('sprinter')

    def setup(self, feature_name, config):
        """ Setup performs the setup required, with the config
        specified """
        if 'rc' in config:
            self.directory.add_to_rc(config['rc'])
        if 'command' in config:
            self.logger.info(lib.call(config['command'], bash=True))

    def update(self, feature_name, config):
        """ Setup performs the setup required, and works with the old
        config is destruction is required """
        if 'rc' in config['target']:
            self.directory.add_to_rc(config['target']['rc'])
        if 'command' in config['target']:
            self.logger.info(lib.call(config['target']['command'], bash=True))

    def destroy(self, feature_name, config):
        """ Destroys an old feature if it is no longer required """
