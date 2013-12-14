import os
import sys
 
from pip.index import PackageFinder
from pip.req import InstallRequirement, RequirementSet
from pip.locations import build_prefix, src_prefix
from pip.exceptions import DistributionNotFound


class PipException(Exception):
    """ Pip exception """


class Pip(object):
    """
    A class to puppet PIP to install new eggs
    """
    requirement_set = None  # the requirement set
    # the package finder
    finder = PackageFinder(find_links=[], index_urls=["http://pypi.python.org/simple/"])
    install_options = []  # the install options with pip
    global_options = []  # the global options with pip

    def __init__(self, egg_directory, install_options=[], global_options=[]):
        self.egg_directory = egg_directory = os.path.abspath(os.path.expanduser(egg_directory))
        self.install_options += ["--home=%s" % egg_directory]
        sys.path += [os.path.join(egg_directory, "lib", "python")]
        self.requirement_set = RequirementSet(
            build_dir=build_prefix,
            src_dir=src_prefix,
            download_dir=None,
            upgrade=True)
    
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
            self.requirement_set.install(self.install_options,
                                         self.global_options)
        except DistributionNotFound:
            self.requirement_set.requirements._keys.remove(egg_name)
            raise PipException()
