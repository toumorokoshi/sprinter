import pytest
from sprinter.core.directory import Directory


@pytest.fixture
def directory(tmpdir):
    return Directory(tmpdir.dirname)
