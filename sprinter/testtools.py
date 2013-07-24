"""
Testing tools to help facilitate sprinter formula testing
"""
from StringIO import StringIO

from mock import Mock


from sprinter.environment import Environment
from sprinter.manifest import Manifest


def create_mock_environment(source_config=None, target_config=None,
                            installed=False):
    """ Create and return a mock environment instance """
    environment = Environment()
    environment.source = (None if not source_config else
                          Manifest(StringIO(source_config), namespace="test"))
    environment.target = (None if not target_config else
                          Manifest(StringIO(target_config), namespace="test"))
    # mocking directory
    environment.directory = Mock(spec=environment.directory)
    environment.directory.bin_path.return_value = "dummy"
    environment.directory.install_directory.return_value = "/tmp/"
    environment.directory.new = not installed
    # mocking injections
    environment.injections = Mock(spec=environment.injections)
    environment.write_manifest = Mock()
    return environment


class FormulaTest(object):

    def setup(self, source_config=None, target_config=None):
        self.environment = create_mock_environment(
            source_config=source_config,
            target_config=target_config
        )
        self.directory = self.environment.directory
        self.environment.instantiate_features()
        self.system = self.environment.system
