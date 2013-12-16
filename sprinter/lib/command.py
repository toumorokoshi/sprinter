from __future__ import unicode_literals
import os
import logging
import subprocess
import sys

COMMAND_WHITELIST = ["cd"]

logger = logging.getLogger(__name__)


class CommandMissingException(Exception):
    """ Return if command doesn't exist """

    def __init__(self, command):
        self.message = "Command %s does not exist in the current path!" % command


def call(command, stdin=None, stdout=subprocess.PIPE, env=os.environ, cwd=None, shell=False,
         output_log_level=logging.INFO, sensitive_info=False):
    """ Better, smarter call logic """
    logger.debug("calling command: %s" % command)
    try:
        args = command if shell else whitespace_smart_split(command)
        kw = {}
        if not shell and not which(args[0], cwd=cwd):
            raise CommandMissingException(args[0])
        if shell:
            kw['shell'] = True
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=stdout, stderr=subprocess.STDOUT,
                                   env=env, cwd=cwd, **kw)
        output = process.communicate(input=stdin)[0]
        if output is not None:
            try:
                logger.log(output_log_level, output.decode('utf-8'))
            except UnicodeDecodeError:
                pass
        return (process.returncode, output)
    except OSError:
        e = sys.exc_info()[1]
        if not sensitive_info:
            logger.exception("Error running command: %s" % command)
            logger.error("Root directory: %s" % cwd)
            if stdin:
                logger.error("stdin: %s" % stdin)
        raise e


def whitespace_smart_split(command):
    """
    Split a command by whitespace, taking care to not split on whitespace within quotes.

    >>> whitespace_smart_split("test this \\\"in here\\\" again")
    ['test', 'this', '"in here"', 'again']
    """
    return_array = []
    s = ""
    in_double_quotes = False
    escape = False
    for c in command:
        if c == '"':
            if in_double_quotes:
                if escape:
                    s += c
                    escape = False
                else:
                    s += c
                    in_double_quotes = False
            else:
                in_double_quotes = True
                s += c
        else:
            if in_double_quotes:
                if c == '\\':
                    escape = True
                    s += c
                else:
                    escape = False
                    s += c
            else:
                if c == ' ':
                    return_array.append(s)
                    s = ""
                else:
                    s += c
    if s != "":
        return_array.append(s)
    return return_array


def which(program, cwd=None):
    if program in COMMAND_WHITELIST:
        return True
    fpath, fname = os.path.split(program)
    if fpath:
        if is_executable(os.path.join((cwd or os.path.curdir), program)):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_executable(exe_file):
                return exe_file

    return None


# From:
# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def is_executable(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
