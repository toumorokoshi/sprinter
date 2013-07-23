"""
Testing tools to help facilitate sprinter formula testing
"""
from StringIO import StringIO

from mock import Mock


from sprinter.environment import Environment
from sprinter.manifest import Manifest
from sprinter.formulabase import FormulaBase


def create_mock_environment(source_config=None, target_config=None):
    """ Create and return a mock environment instance """
    environment = Environment()
    environment.source = (None if not source_config else
                          Manifest(StringIO(source_config), namespace="test"))
    environment.target = (None if not target_config else
                          Manifest(StringIO(target_config), namespace="test"))
    return environment


class FormulaTest(object):

    def setup(self, source_config=None, target_config=None):
        self.environment = create_mock_environment(
            source_config=source_config,
            target_config=target_config
        )
        self.environment.directory = Mock(spec=self.environment.directory)
        self.directory = self.environment.directory
        self.directory.bin_path.return_value = "dummy"
        self.directory.install_directory.return_value = "/tmp/"
        self.directory.new = True
        self.environment.instantiate_features()
        self.system = self.environment.system


class DummyFormula(FormulaBase):
    """ A dummy formula object """
