from mock import Mock
from StringIO import StringIO

from sprinter.environment import Environment
from sprinter.manifest import Manifest


class TestFormula(object):
    """
    A test class to provide utility methods for testing sprinter
    formulas.
    """
    def __init__(self, formula_config=None):
        self.formula_config = formula_config
        self.formula_manifest = Manifest(StringIO(formula_config), namespace="test")

    def setup(self):
        environment = Environment()
        environment.lib = Mock()
        self.environment = environment

    def install(self, feature_name):
        """ Run an install of a feature """
        self.environment.install_formula(feature_name, self.formula_manifest)
