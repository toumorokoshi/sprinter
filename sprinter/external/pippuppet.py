from __future__ import unicode_literals
import os
import shutil
import sys

from pip.download import PipSession
from pip.index import PackageFinder
from pip.req import InstallRequirement, RequirementSet
from pip.locations import build_prefix, src_prefix
from pip.exceptions import DistributionNotFound

# we have to get the major, minor version because
# we're using the "prefix scheme" of python layouts:
# https://docs.python.org/2/install/#alternate-installation-unix-the-prefix-scheme
# this is to support the brew (OSX) install of Python.
# https://github.com/Homebrew/homebrew/blob/master/share/doc/homebrew/Homebrew-and-Python.md
PYTHON_VERSION = "{0}.{1}".format(
    sys.version_info[0], sys.version_info[1]
)


class PipException(Exception):
    """ Pip exception """


class Pip(object):
    """
    A class to puppet PIP to install new eggs
    """
    requirement_set = None  # the requirement set
    # the package finder
    finder = PackageFinder(find_links=[],
                           index_urls=["http://pypi.python.org/simple/"],
                           session=PipSession())

    def __init__(self, egg_directory):
        self.egg_directory = egg_directory = os.path.abspath(os.path.expanduser(egg_directory))
        sys.path += [os.path.join(egg_directory, "lib",
                                  "python" + PYTHON_VERSION, "site-packages")]
        self.requirement_set = RequirementSet(
            build_dir=build_prefix,
            src_dir=src_prefix,
            download_dir=None,
            upgrade=True,
            session=PipSession()
        )

    def delete_all_eggs(self):
        """ delete all the eggs in the directory specified """
        path_to_delete = os.path.join(self.egg_directory, "lib", "python")
        if os.path.exists(path_to_delete):
            shutil.rmtree(path_to_delete)

    def install_egg(self, egg_name):
        """ Install an egg into the egg directory """
        if not os.path.exists(self.egg_directory):
            os.makedirs(self.egg_directory)
        self.requirement_set.add_requirement(
            InstallRequirement.from_line(egg_name, None))
        try:
            self.requirement_set.prepare_files(self.finder,
                                               force_root_egg_info=False,
                                               bundle=False)
            self.requirement_set.install(['--prefix=' + self.egg_directory])
        except DistributionNotFound:
            self.requirement_set.requirements._keys.remove(egg_name)
            raise PipException()
