import unittest
from StringIO import StringIO

from mock import Mock

from sprinter.environment import Environment
from sprinter.manifest import Manifest


class TestFormula(unittest.TestCase):
    """
    A test class to provide utility methods for testing sprinter
    formulas.
    """
    def __init__(self, formula_class, source_config=None, target_config=None):
        self.source = (None if not source_config else
                       Manifest(StringIO(source_config), namespace="test"))
        self.target = (None if not target_config else
                       Manifest(StringIO(target_config), namespace="test"))
        self.formula_class = formula_class

    def setup(self):
        environment = Environment()
        environment.source = self.source
        environment.target = self.target
        environment.lib = Mock(spec=environment.lib)
        self.environment = environment
        self.instance = self.formula_class(environment)

    def install(self, feature_name):
        """ Run an install of a feature """
        self.environment.install_formula(feature_name, self.instance)

    def update(self, feature_name):
        """ Run an update of a feature """
        self.environment.update_formula(feature_name, self.instance)

    def remove(self, feature_name):
        """ Run an remove of a feature """
        self.environment.remove_formula(feature_name, self.instance)

    def activate(self, feature_name):
        """ Run an activate of a feature """
        self.environment.activate_formula(feature_name, self.instance)

    def deactivate(self, feature_name):
        """ Run a deactivate of a feature """
        self.environment.deactivate_formula(feature_name, self.instance)
