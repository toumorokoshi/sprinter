"""
A set of compatibility methods
"""
import sys
from six.moves import configparser


def create_configparser():
    if sys.version_info > (3, 0):
        return configparser.RawConfigParser(strict=True)
    else:
        return configparser.RawConfigParser()


if sys.version_info > (3, 0):
    def _unicode(s):
        return s
else:
    def _unicode(s):
        """ return the string converted to unicode. """
        if not isinstance(s, unicode):
            s = s.decode("utf8")
        return s
