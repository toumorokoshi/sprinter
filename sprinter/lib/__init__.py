"""
Library module for sprinter. To handle a lot of the typical
features of the library.

"""
from __future__ import unicode_literals
import logging
import re

from getpass import getpass

from six import string_types
from six.moves import input

logger = logging.getLogger(__name__)

DOMAIN_REGEX = re.compile("^https?://(\w+\.)?\w+\.\w+\/?")
COMMAND_WHITELIST = ["cd"]
BYTE_CHUNKS = 50
BOOLEAN_DEFAULTS = {
    'bool': { True: ' (TRUE|false): ', False: '(true|FALSE): ' },
    'y_n': { True: ' (Y|n): ', False: ' (y|N): ' },
    'yes_no': { True: ' (YES|no): ', False: ' (yes|NO): ' }
}

from .extract import extract_dmg, extract_targz, extract_zip, remove_path, ExtractException
from .command import call, whitespace_smart_split, which, is_executable, CommandMissingException
from .module import get_subclass_from_module
from .request import CertificateException, BadCredentialsException, authenticated_get, cleaned_request


def prompt(prompt_string, default=None, secret=False, boolean=False, bool_type=None):
    """
    Prompt user for a string, with a default value

    * secret converts to password prompt
    * boolean converts return value to boolean, checking for starting with a Y
    """
    if boolean or bool_type in BOOLEAN_DEFAULTS:
        if bool_type is None:
            bool_type = 'y_n'
        default_msg = BOOLEAN_DEFAULTS[bool_type][is_affirmative(default)]
    else:
        default_msg = " (default {val}): "
    prompt_string += (default_msg.format(val=default) if default else ": ")
    if secret:
        val = getpass(prompt_string)
    else:
        val = input(prompt_string)
    val = (val if val else default)
    if boolean:
        val = val.lower().startswith('y')
    return val


def is_affirmative(phrase):
    """
    Determine if a phrase is in the affirmative
    * start with a t or y, case insensitive
    """
    if isinstance(phrase, string_types):
        return phrase.lower()[0] in ['t', 'y']
    else:
        return phrase


def insert_environment_osx(**environment_variables):
    """ Inject the environment variables desired into the osx environment """


"""
def get_file_owner_group()
    stat_info = os.stat('/path')
    uid = stat_info.st_uid
    gid = stat_info.st_gid
    print uid, gid

    user = pwd.getpwuid(uid)[0]
    group = grp.getgrgid(gid)[0]
    print user, group
"""
