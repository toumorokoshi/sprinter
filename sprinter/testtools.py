"""
Testing tools to help facilitate sprinter formula testing
"""
from __future__ import unicode_literals
from io import StringIO

from mock import Mock, patch
from contextlib import contextmanager
import shutil
import tempfile


from sprinter.environment import Environment
from sprinter.formula.base import FormulaBase
from sprinter.core import PHASE, load_manifest, FeatureDict
from sprinter.core.globals import create_default_config

MOCK_GLOBAL_CONFIGURATION = """
"""


class MockEnvironment(object):

    def __init__(self, *args, **kw):
        self.environment, self.temp_directory = create_mock_environment(*args, **kw)

    def __enter__(self):
        return self.environment

    def __exit__(self, instance_type, value, traceback):
        shutil.rmtree(self.temp_directory)


def create_mock_environment(source_config=None, target_config=None,
                            global_config=None, mock_formulabase=None):
        temp_directory = tempfile.mkdtemp()
        environment = Environment(root=temp_directory,
                                  sprinter_namespace='test',
                                  global_config=(global_config or create_default_config()))
        environment.namespace = "test"
        if source_config:
            environment.source = load_manifest(StringIO(source_config), namespace="test")

        if target_config:
            environment.target = load_manifest(StringIO(target_config), namespace="test")
        
        environment.warmup()
        # TODO: implement sandboxing so no need to mock these
        environment.injections.commit = Mock()
        environment.global_injections.commit = Mock()
        environment.write_manifest = Mock()
        if mock_formulabase:
            formula_dict = {'sprinter.formula.base': mock_formulabase}
            environment.features = FeatureDict(environment,
                                               environment.source, environment.target,
                                               environment.global_path,
                                               formula_dict=formula_dict)
        return environment, temp_directory
    

def create_mock_formulabase():
    """ Generate a formulabase object that does nothing, and returns no errors """
    mock_formulabase = Mock(spec=FormulaBase)
    mock_formulabase.side_effect = lambda *args, **kw: mock_formulabase
    mock_formulabase.should_run.return_value = True
    mock_formulabase.resolve.return_value = None
    mock_formulabase.prompt.return_value = None
    mock_formulabase.sync.return_value = None
    for phase in PHASE.values:
        setattr(mock_formulabase, phase.name, Mock(return_value=None))

    return mock_formulabase


class FormulaTest(object):

    def setup(self, **kw):
        self.environment, self.temp_directory = create_mock_environment(**kw)
        # adding some extra mocking
        self.directory = self.environment.directory
        self.environment.instantiate_features()


@contextmanager
def set_os_types(osx=False, debian=False, fedora=False):
    with patch('sprinter.lib.system.is_osx') as is_osx:
        is_osx.return_value = osx
        with patch('sprinter.lib.system.is_debian') as is_debian:
            is_debian.return_value = debian
            with patch('sprinter.lib.system.is_fedora') as is_fedora:
                is_fedora.return_value = fedora
                yield
