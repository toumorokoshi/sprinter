"""
Utility methods for brew
"""
import os
from sprinter.lib import extract_targz
from sprinter.core import LOGGER

HOMEBREW_URL = "http://github.com/mxcl/homebrew/tarball/master"


def install_brew(target_path):
    """ Install brew to the target path """
    if not os.path.exists(target_path):
        try:
            os.makedirs(target_path)
        except OSError:
            LOGGER.warn("Unable to create directory %s for brew." % target_path)
            LOGGER.warn("Skipping...")
            return
    extract_targz(HOMEBREW_URL, target_path, remove_common_prefix=True)
