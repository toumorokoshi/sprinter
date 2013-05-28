"""
Utility methods for brew
"""
from sprinter.lib import extract_targz

HOMEBREW_URL = "https://github.com/mxcl/homebrew/tarball/master"


def install_brew(target_path):
    """ Install brew to the target path """
    extract_targz(HOMEBREW_URL, target_path, remove_common_prefix=True)


def install_brew_package(package, brew_executable="brew"):
    """ Install a brew package """
    "%s install %s" % (brew_executable, package)
