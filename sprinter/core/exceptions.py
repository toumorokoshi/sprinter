"""
This lists all the exceptions in sprinter
"""
from __future__ import unicode_literals


class SprinterException(Exception):
    """ For generic sprinter exceptions """


class FormulaException(Exception):
    """ For a generic exception with a formula """


class CommandMissingException(Exception):
    """ Return if command doesn't exist """

    def __init__(self, command):
        self.message = "Command %s does not exist in the current path!" % command


class BadCredentialsException(Exception):
    """ Returned if the credentials are incorrect """


class CertificateException(Exception):
    """ Returned if the certificates are incorrect """


class ExtractException(Exception):
    """ Returned if there was an issue with extracting a package """
