import pytest
from sprinter.core.directory import Directory
from sprinter.core.link_dir import LinkDir


@pytest.fixture
def directory(tmpdir):
    return Directory(tmpdir.mkdir("directory").strpath)


@pytest.fixture
def link_dir(tmpdir):
    return LinkDir(tmpdir.join("link").strpath)
