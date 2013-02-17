"""
Recipe base is an abstract base class outlining the method required
and some documentation on what they should provide.
"""

from abc import ABCMeta, abstractmethod


class RecipeBase:
    __metaclass__ = ABCMeta

    def __init__(self, environment):
        self.environment = environment

    @abstractmethod
    def setup(self, feature_name, config):
        """ Setup performs the setup required, with the config
        specified """
        pass

    @abstractmethod
    def update(self, feature_name, config):
        """ Setup performs the setup required, and works with the old
        config is destruction is required """
        pass

    @abstractmethod
    def destroy(self, feature_name, old_config):
        """ Destroys an old feature if it is no longer required """
        pass
