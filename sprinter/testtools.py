"""
Testing tools to help facilitate sprinter formula testing
"""
from __future__ import unicode_literals
from io import StringIO

from mock import Mock
import shutil
import tempfile


from sprinter.environment import Environment
from sprinter.formula.base import FormulaBase
from sprinter.core import Injections, PHASE, load_manifest
from sprinter.core.globals import create_default_config

MOCK_GLOBAL_CONFIGURATION = """
"""


class MockEnvironment(object):

    def __init__(self, source_config=None, target_config=None, global_config=None):
        self.temp_directory = tempfile.mkdtemp()
        self.environment = Environment(root=self.temp_directory,
                                       sprinter_namespace='test',
                                       global_config=(global_config or create_default_config()))
        if source_config:
            self.environment.source = load_manifest(StringIO(source_config), namespace="test")

        if target_config:
            self.environment.target = load_manifest(StringIO(target_config), namespace="test")
        
        self.environment.warmup()
        # TODO: implement sandboxing so no need to mock these
        self.environment.injections.commit = Mock()
        self.environment.global_injections.commit = Mock()
        self.environment.write_manifest = Mock()

    def __enter__(self):
        return self.environment

    def __exit__(self, instance_type, value, traceback):
        shutil.rmtree(self.temp_directory)


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
                              root=root)
    environment.source = (None if not source_config else
                          load_manifest(StringIO(source_config), namespace="test"))
    environment.target = (None if not target_config else
                          load_manifest(StringIO(target_config), namespace="test"))
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
    environment.write_manifest = Mock()
    return environment


def create_mock_formulabase():
    """ Generate a formulabase object that does nothing, and returns no errors """
    mock_formulabase = Mock(spec=FormulaBase)
    mock_formulabase.side_effect = lambda *args, **kw: mock_formulabase
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
