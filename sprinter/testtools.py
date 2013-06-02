"""
Testing tools to help facilitate sprinter formula testing
"""
from StringIO import StringIO


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
