"""
This lists all the exceptions in sprinter
"""


class SprinterException(Exception):
    """ For generic sprinter exceptions """


class CommandMissingException(Exception):
    """ Return if command doesn't exist """

    def __init__(self, command):
        self.message = "Command %s does not exist in the current path!" % command


class BadCredentialsException(Exception):
    """ Returned if the credentials are incorrect """
