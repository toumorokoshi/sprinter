import pytest
from sprinter.next.environment.injections import Injections


@pytest.fixture
def injections():
    return Injections("testinjection")
