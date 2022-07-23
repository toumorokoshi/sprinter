import pytest
from mock import Mock


@pytest.yield_fixture
def mock_feature():
    return Mock()
