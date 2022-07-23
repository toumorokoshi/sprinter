import os
import shutil
import tempfile
import pytest

from sprinter.next.environment.injections import Injections

TEST_CONTENT = """
Testing abc.

#OVERRIDE
here is an override string. it should appear at the bottom.
#OVERRIDE
"""

TEST_OVERRIDE_CONTENT = """
Testing abc.

#testinjection
injectme
#testinjection

#OVERRIDE
here is an override string. it should appear at the bottom.
#OVERRIDE
"""

PERMANENT_STRING = "this should stay no matter what."
TEST_INJECTION = "this should stay temporarily"


@pytest.fixture
def test_file(tmpdir):
    f = tmpdir.join("test")
    f.write(PERMANENT_STRING)
    return f


@pytest.fixture
def injections():
    return Injections("testinjection", override="OVERRIDE")


def test_backup_file_created(test_file, injections):
    """test a backup file is created."""
    injections.inject(test_file.strpath, TEST_INJECTION)
    injections.commit()
    assert os.path.exists(test_file.strpath + ".sprinter.bak")
    os.unlink(test_file.strpath + ".sprinter.bak")
    injections.clear(test_file.strpath)
    injections.commit()
    assert os.path.exists(test_file.strpath + ".sprinter.bak")


def test_injection(test_file, injections):
    """test a complete injection workflow."""
    injections.inject(test_file.strpath, TEST_INJECTION)
    injections.commit()
    assert (
        test_file.read().count(TEST_INJECTION) > 0
    ), "Injection was not injected properly!"
    assert (
        test_file.read().count(TEST_INJECTION) == 1
    ), "Multiple injections were found!"
    assert (
        test_file.read().find(PERMANENT_STRING) != -1
    ), "Permanent string was removed on inject!"
    injections.clear(test_file.strpath)
    injections.commit()
    assert (
        test_file.read().find(TEST_INJECTION) == -1
    ), "Injection was not cleared properly!"
    assert (
        test_file.read().find(PERMANENT_STRING) != -1
    ), "Permanent string was removed on clear!"


def test_similar_injectionname(test_file, injections):
    injections.inject(test_file.strpath, TEST_INJECTION)
    injections.commit()
    SIMILAR_INJECTION = "This is a similar injection"
    i_similiar = Injections("testinjectionsagain")
    i_similiar.inject(test_file.strpath, SIMILAR_INJECTION)
    i_similiar.commit()
    assert (
        test_file.read().count(SIMILAR_INJECTION) > 0
    ), "Similar injection was removed!"
    assert (
        test_file.read().count(SIMILAR_INJECTION) == 1
    ), "Multiple injections were found!"
    injections.clear(test_file.strpath)
    injections.commit()
    assert (
        test_file.read().find(TEST_INJECTION) == -1
    ), "Injection was not cleared properly!"
    assert (
        test_file.read().find(SIMILAR_INJECTION) > 0
    ), "Similar Injection was incorrectly cleared!"


def test_override(injections):
    """Test the override functionality"""
    c = injections.inject_content(TEST_CONTENT, "injectme")
    assert c == TEST_OVERRIDE_CONTENT, "Override result is different from expected."


def test_unicode():
    """Test the unicode functionality"""
    i = Injections("\xf0\x9f\x86\x92", override="OVERRIDE")
    i.inject_content(TEST_CONTENT, "injectme")


def test_injected(test_file, injections):
    """Test the injected method to determine if a file has already been injected..."""
    assert not injections.injected(
        test_file.strpath
    ), "Injected check returned true when not injected yet."
    injections.inject(test_file.strpath, TEST_INJECTION)
    injections.commit()
    assert injections.injected(test_file.strpath), "Injected check returned false"


def test_in_noninjected_file(test_file, injections):
    """
    in_noninjected_file should return true if a string exists
    non-injected and false it only exists in injected
    """
    assert not injections.injected(
        test_file.strpath
    ), "Injected check returned true when not injected yet."
    injections.inject(test_file.strpath, TEST_INJECTION)
    injections.commit()
    assert injections.in_noninjected_file(test_file.strpath, PERMANENT_STRING)
    assert not injections.in_noninjected_file(test_file.strpath, TEST_INJECTION)


def test_injected_injects_after_overrides(injections):
    """
    re-injecting into a file will come after all other content
    """
    ORIGINAL_STRING = """
#testinjection
injectme
#testinjection

#OVERRIDE
overidden content
#OVERRIDE

non-override content
    """.strip()
    c = injections.inject_content(ORIGINAL_STRING, "injectme")
    assert c.find("injectme") > c.find("non-override content")


def test_created(tmpdir, injections):
    """Test the injection creates a file if it does not exist"""
    new_file = os.path.join(tmpdir.strpath, "testcreated")
    injections.inject(new_file, TEST_INJECTION)
    injections.commit()
    assert os.path.exists(new_file), "File was not generated on injection!"


def test_clear_nonexistent_file(tmpdir):
    """clear should not create a file"""
    i = Injections("testinjection")
    new_file = os.path.join(tmpdir.strpath, "dontcreateme")
    i.clear(new_file)
    i.commit()
    assert not os.path.exists(new_file)
