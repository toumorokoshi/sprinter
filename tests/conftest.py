import pytest
from mock import Mock
from sprinter.core.directory import Directory
from sprinter.formula.base import FormulaBase
from sprinter.feature import Feature


@pytest.fixture
def directory(tmpdir):
    return Directory(tmpdir.dirname)


@pytest.fixture
def environment(directory):
    mock = Mock()
    mock.directory = directory
    return mock


@pytest.fixture
def formula_base(environment):
    return FormulaBase(environment, "foo")


@pytest.fixture
def feature(formula_base):
    return Feature(formula_base)
