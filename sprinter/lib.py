"""
Library module for sprinter. To handle a lot of the typical
features of the library.

"""
import zipfile
import gzip
import logging
import inspect
import imp
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import requests
from io import StringIO

from getpass import getpass
from subprocess import PIPE, STDOUT

from six import string_types
from six.moves import input

from sprinter.exceptions import (CommandMissingException,
                                 BadCredentialsException,
                                 CertificateException,
                                 ExtractException,
                                 SprinterException)
from sprinter.core import LOGGER

DOMAIN_REGEX = re.compile("^https?://(\w+\.)?\w+\.\w+\/?")
COMMAND_WHITELIST = ["cd"]
BYTE_CHUNKS = 50


def get_subclass_from_module(module, parent_class):
    """
    Get a subclass of parent_class from the module at module

    get_subclass_from_module performs reflection to find the first class that
    extends the parent_class in the module path, and returns it.
    """
    try:
        r = __recursive_import(module)
        member_dict = dict(inspect.getmembers(r))
        sprinter_class = parent_class
        for v in member_dict.values():
            if inspect.isclass(v) and issubclass(v, parent_class) and v != parent_class:
                if sprinter_class is parent_class:
                    sprinter_class = v
        if sprinter_class is None:
            raise SprinterException("No subclass %s that extends %s exists in classpath!" % (module, str(parent_class)))
        return sprinter_class
    except ImportError:
        e = sys.exc_info()[1]
        raise e


def call(command, stdin=None, stdout=PIPE, env=os.environ, cwd=None, shell=False,
         output_log_level=logging.INFO, logger=LOGGER, sensitive_info=False):
    """ Better, smarter call logic """
    logger.debug("calling command: %s" % command)
    try:
        args = command if shell else whitespace_smart_split(command)
        kw = {}
        if not shell and not which(args[0], cwd=cwd):
            raise CommandMissingException(args[0])
        if shell:
            kw['shell'] = True
        process = subprocess.Popen(args, stdin=PIPE, stdout=stdout, stderr=STDOUT,
                                   env=env, cwd=cwd, **kw)
        output = process.communicate(input=stdin)[0]
        logger.log(output_log_level, output)
        return (process.returncode, output)
    except OSError:
        e = sys.exc_info()[1]
        if not sensitive_info:
            logger.exception("Error running command: %s" % command)
            logger.error("Root directory: %s" % cwd)
            if stdin:
                logger.error("stdin: %s" % stdin)
        raise e


def __process(arg):
    """
    Process args for a bash shell
    """
    # assumes it's wrapped in quotes, or is a flag
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


def authenticated_get(username, password, url, verify=True):
    """
    Perform an authorized query to the url, and return the result
    """
    try:
        response = requests.get(url, auth=(username, password), verify=verify)
        if response.status_code == 401:
            raise BadCredentialsException(
                "Unable to authenticate user %s to %s with password provided!"
                % (username, url))
    except requests.exceptions.SSLError:
        raise CertificateException("Unable to verify certificate at %s!" % url)
    return response.content


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
        val = input(prompt_string)
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
    if isinstance(phrase, string_types):
        return phrase.lower()[0] in ['t', 'y']
    else:
        return phrase


# From:
# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program, cwd=None):
    if program in COMMAND_WHITELIST:
        return True
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(os.path.join((cwd or os.path.curdir), program)):
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
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        gz = gzip.GzipFile(fileobj=io.BytesIO(requests.get(url).content))
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
    except OSError:
        e = sys.exc_info()[1]
        raise ExtractException(str(e))
    except IOError:
        e = sys.exc_info()[1]
        raise ExtractException(str(e))


def extract_zip(url, target_dir, remove_common_prefix=False, overwrite=False):
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        memory_file = io.BytesIO(requests.get(url).content)
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
    except OSError:
        raise ExtractException()
    except IOError:
        raise ExtractException()


def extract_dmg(url, target_dir, remove_common_prefix=False, overwrite=False):
    if remove_common_prefix:
        raise Exception("Remove common prefix for zip not implemented yet!")
    tmpdir = tempfile.mkdtemp()
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        temp_file = os.path.join(tmpdir, "temp.dmg")
        with open(temp_file, 'bw+') as fh:
            fh.write(requests.get(url).content)
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
    except OSError:
        raise ExtractException()
    except IOError:
        raise ExtractException()
    finally:
        call("hdiutil unmount /Volumes/a")
        shutil.rmtree(tmpdir)


def remove_path(target_path):
    """ Delete the target path """
    if os.path.isdir(target_path):
        shutil.rmtree(target_path)
    else:
        os.unlink(target_path)


def insert_environment_osx(**environment_variables):
    """ Inject the environment variables desired into the osx environment """


def _determine_overwrite(prompt, overwrite, path):
    """ Determines if an overwrite is desired """
    if overwrite:
        return True
    elif prompt:
        return prompt("Path %s already exist! Overwrite?" % path, boolean=True)
    return True


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
