"""
Testing tools to help facilitate sprinter formula testing
"""
from __future__ import unicode_literals
from io import StringIO

from mock import Mock


from sprinter.environment import Environment
from sprinter.formulabase import FormulaBase
from sprinter.injections import Injections
from sprinter.manifest import Manifest
from sprinter.core import PHASE

MOCK_GLOBAL_CONFIGURATION = """
"""


def create_mock_environment(source_config=None,
                            target_config=None,
                            installed=False,
                            global_config=MOCK_GLOBAL_CONFIGURATION,
                            root=None,
                            mock_injections=True,
                            mock_global_injections=True,
                            mock_system=True,
                            mock_directory=True):
    """ Create and return a mock environment instance """
    environment = Environment(global_config=global_config,
                              write_files=False,
                              root=root)
    environment.source = (None if not source_config else
                          Manifest(StringIO(source_config), namespace="test"))
    environment.target = (None if not target_config else
                          Manifest(StringIO(target_config), namespace="test"))
    # mocking directory
    if mock_directory:
        environment.directory = Mock(spec=environment.directory)
        environment.directory.bin_path.return_value = "dummy"
        environment.directory.install_directory.return_value = "/tmp/"
        environment.directory.new = not installed
    # mocking injections
    if mock_injections:
        environment.injections = Mock(spec=Injections)
    # mocking global injections
    if mock_global_injections:
        environment.global_injections = Mock(spec=Injections)
    # mocking system (we will always test as if the system is debian, unless explicitly specified)
    if mock_system:
        environment.system = Mock(spec=environment.system)
        environment.system.isDebianBased.return_value = True
        environment.system.isOSX.return_value = False
        environment.system.isFedoraBased.return_value = False
    environment.write_manifest = Mock()
    return environment


def create_mock_formulabase():
    """ Generate a formulabase object that does nothing, and returns no errors """
    mock_formulabase = Mock(spec=FormulaBase)
    mock_formulabase.resolve.return_value = None
    mock_formulabase.prompt.return_value = None
    mock_formulabase.sync.return_value = None
    for phase in PHASE.values:
        setattr(mock_formulabase, phase.name, Mock(return_value=None))
    return mock_formulabase


class FormulaTest(object):

    def setup(self, source_config=None, target_config=None):
        self.environment = create_mock_environment(
            source_config=source_config,
            target_config=target_config
        )
        self.directory = self.environment.directory
        self.environment.instantiate_features()
        self.system = self.environment.system
