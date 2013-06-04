"""
Testing tools to help facilitate sprinter formula testing
"""
from StringIO import StringIO

from mock import Mock


from sprinter.environment import Environment
from sprinter.manifest import Manifest


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
        self.environment.lib = Mock(spec=self.environment.lib)
        self.environment.directory = Mock(spec=self.environment.directory)
        self.lib = self.environment.lib
        self.directory = self.environment.directory
        self.directory.bin_path = Mock(return_value="dummy")
        self.directory.install_directory = Mock(return_value="/tmp/")
