"""
Library module for sprinter. To handle a lot of the typical
features of the library.

"""
import inspect
import imp
import os
import re
import subprocess
import urllib2
from StringIO import StringIO
from base64 import b64encode

from getpass import getpass
from subprocess import PIPE, STDOUT

from sprinter.formulabase import FormulaBase

DOMAIN_REGEX = re.compile("^https?://(\w+\.)?\w+\.\w+\/?")


class CommandMissingException(Exception):
    """ Return if command doesn't exist """

    def __init__(self, command):
        self.message = "Command %s does not exist in the current path!" % command


def get_formula_class(formula, environment):
    """
    Get the formula name and return an instance The formula path is a
    path to the module. get_formula_class performs reflection to find
    the first class that extends formulabase, and that is the class
    that an instance of it gets returned.
    """
    try:
        r = __recursive_import(formula)
        member_dict = dict(inspect.getmembers(r))
        for v in member_dict.values():
            if inspect.isclass(v) and issubclass(v, FormulaBase) and v != FormulaBase:
                return v(environment)
        raise Exception("No formula %s exists in classpath!" % formula)
    except ImportError as e:
        raise e


def call(command, stdin=None, env=os.environ, cwd=None, bash=False):
    if not bash:
        args = __whitespace_smart_split(command)
        if not which(args[0]):
            raise CommandMissingException(args[0])
        p = subprocess.Popen(args, stdin=PIPE, stderr=STDOUT, env=env, cwd=cwd)
        p.communicate(input=stdin)[0]
        return p.returncode
    else:
        command = " ".join([__process(arg) for arg in __whitespace_smart_split(command)])
        return subprocess.call(command, shell=True, executable='/bin/bash', cwd=cwd, env=env)


def __process(arg):
    """
    Process args for a bash shell
    """
    # assumes it's wrappen in quotes, or is a flag
    if arg[0] in ["'", '"', '-']:
        return arg
    else:
        return __escape(arg)


def __escape(s):
    """
    Custom escape module for bash
    """
    buf = StringIO()
    for c in s:
        if c in ['(', ')', ':']:
            buf.write("\\" + c)
        else:
            buf.write(c)
    return buf.getvalue()


def __whitespace_smart_split(command):
    """
    Split a command by whitespace, taking care to not split on whitespace within quotes.

    >>> __whitespace_smart_split("test this \\\"in here\\\" again")
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


def authenticated_get(username, password, url):
    """
    Perform an authorized query to the url, and return the result
    """
    request = urllib2.Request(url)
    base64string = b64encode((b"%s:%s" % (username, password)).decode("ascii"))
    request.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(request)
    return result.read()


def prompt(prompt_string, default=None, secret=False, boolean=False):
    """
    Prompt user for a string, with a default value

    * secret converts to password prompt
    * boolean converts return value to boolean, checking for starting with a Y
    """
    prompt_string += (" (default %s): " % default if default else ": ")
    if secret:
        val = getpass(prompt_string)
    else:
        val = raw_input(prompt_string)
    val = (val if val else default)
    if boolean:
        val = val.lower().startswith('y')
    return val


def __recursive_import(module_name):
    """
    Recursively looks for and imports the names, returning the
    module desired

    >>> __recursive_import("sprinter.formulas.unpack") # doctest: +ELLIPSIS
    <module 'unpack' from '...'>

    currently module with relative imports don't work.
    """
    names = module_name.split(".")
    path = None
    module = None
    while len(names) > 0:
        if module:
            path = module.__path__
        name = names.pop(0)
        (module_file, pathname, description) = imp.find_module(name, path)
        module = imp.load_module(name, module_file, pathname, description)
    return module


# From:
# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

if __name__ == '__main__':
    import doctest
    doctest.testmod()
