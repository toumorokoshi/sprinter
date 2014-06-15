from nose.tools import ok_
from sprinter.lib.command import CommandMissingException


def test_exception_formatting():
    """ command missing exception should be formatted properly """
    exception = CommandMissingException("foo")
    ok_("foo" in str(exception))
