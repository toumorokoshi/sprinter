"""
Library module for sprinter. To handle a lot of the typical
features of the library.

"""
import zipfile
import gzip
import inspect
import imp
import io
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib2
import urllib
from StringIO import StringIO
from base64 import b64encode

from getpass import getpass
from subprocess import PIPE, STDOUT

from sprinter.formulabase import FormulaBase
from sprinter.exceptions import CommandMissingException, BadCredentialsException

DOMAIN_REGEX = re.compile("^https?://(\w+\.)?\w+\.\w+\/?")
COMMAND_WHITELIST = ["cd"]


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
        sprinter_class = FormulaBase
        for v in member_dict.values():
            if inspect.isclass(v) and issubclass(v, FormulaBase) and v != FormulaBase:
                if sprinter_class is FormulaBase:
                    sprinter_class = v
        if sprinter_class is None:
            raise Exception("No formula %s exists in classpath!" % formula)
        return sprinter_class(environment)
    except ImportError as e:
        raise e


def call(command, stdin=None, env=os.environ, cwd=None, bash=False):
    if not bash:
        args = whitespace_smart_split(command)
        if not which(args[0]):
            raise CommandMissingException(args[0])
        p = subprocess.Popen(args, stdin=PIPE, stderr=STDOUT, env=env, cwd=cwd)
        p.communicate(input=stdin)[0]
        return p.returncode
    else:
        command = " ".join([__process(arg) for arg in whitespace_smart_split(command)])
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


def whitespace_smart_split(command):
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
    try:
        request = urllib2.Request(url)
        base64string = b64encode((b"%s:%s" % (username, password)).decode("ascii"))
        request.add_header("Authorization", "Basic %s" % base64string)
        result = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        if e.code == 401:
            raise BadCredentialsException(
                "Unable to authenticate user %s to %s with password provided!"
                % (username, url))
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


def is_affirmative(phrase):
    """
    Determine if a phrase is in the affirmative
    * start with a t or y, case insensitive
    """
    return phrase.lower()[0] in ['t', 'y']


# From:
# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):
    if program in COMMAND_WHITELIST:
        return True
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


def extract_targz(url, target_dir, remove_common_prefix=False, overwrite=False):
    """ extract a targz and install to the target directory """
    gz = gzip.GzipFile(fileobj=StringIO(urllib.urlopen(url).read()))
    tf = tarfile.TarFile(fileobj=gz)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    common_prefix = os.path.commonprefix(tf.getnames())
    if not common_prefix.endswith('/'):
        common_prefix += "/"
    for tfile in tf.getmembers():
        if remove_common_prefix:
            tfile.name = tfile.name.replace(common_prefix, "", 1)
        if tfile.name != "":
            target_path = os.path.join(tfile, target_dir)
            if target_path != target_dir and os.path.exists(target_path):
                if overwrite:
                    remove_path(target_path)
                else:
                    return
            tf.extract(tfile, target_dir)


def extract_zip(url, target_dir, remove_common_prefix=False, overwrite=False):
    memory_file = io.BytesIO(urllib.urlopen(url).read())
    zip_file = zipfile.ZipFile(memory_file)
    common_prefix = os.path.commonprefix(zip_file.namelist())
    for zip_file_info in zip_file.infolist():
        target_path = zip_file_info.filename
        if remove_common_prefix:
            target_path = target_path.replace(common_prefix, "", 1)
        if target_path != "":
            target_path = os.path.join(target_dir, target_path)
            if target_path != target_dir and os.path.exists(target_path):
                if overwrite:
                    remove_path(target_path)
                else:
                    return
            zip_file.extract(zip_file_info, target_path)


def extract_dmg(url, target_dir, remove_common_prefix=False, overwrite=False):
    if remove_common_prefix:
        raise("Remove common prefix for zip not implemented yet!")
    tmpdir = tempfile.mkdtemp()
    try:
        temp_file = os.path.join(tmpdir, "temp.dmg")
        urllib.urlretrieve(url, temp_file)
        call("hdiutil attach %s -mountpoint /Volumes/a/" % temp_file)
        for f in os.listdir("/Volumes/a/"):
            if not f.startswith(".") and f != ' ':
                source_path = os.path.join("/Volumes/a", f)
                target_path = os.path.join(target_dir, f)
                if target_path != target_dir and os.path.exists(target_path):
                    if overwrite:
                        remove_path(target_path)
                    else:
                        return
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, target_path)
                else:
                    shutil.copy(source_path, target_path)
    finally:
        call("hdiutil unmount /Volumes/a")
        shutil.rmtree(tmpdir)


def remove_path(target_path):
    """ Delete the target path """
    if os.path.isdir(target_path):
        shutil.rmtree(target_path)
    else:
        os.unlink(target_path)


def _determine_overwrite(prompt, overwrite, path):
    """ Determines if an overwrite is desired """
    if overwrite:
        return True
    elif prompt:
        return prompt("Path %s already exist! Overwrite?" % path, boolean=True)
    return True

if __name__ == '__main__':
    import doctest
    doctest.testmod()
