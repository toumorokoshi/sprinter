"""
Utility methods for brew
"""
import os
import logging
import getpass
from sprinter.lib import extract_targz
from sprinter.core import LOGGER
from sprinter import lib

HOMEBREW_URL = "https://github.com/mxcl/homebrew/tarball/master"


def install_brew(target_path):
    """ Install brew to the target path """
    if not os.path.exists(target_path):
        try:
            os.makedirs(target_path)
        except OSError:
            LOGGER.warn("Unable to create directory %s for brew." % target_path + 
                        " Trying sudo...")
            lib.call("sudo mkdir -p %s" % target_path, stdout=None,
                     output_log_level=logging.DEBUG)
            lib.call("sudo chown %s %s" % (getpass.getuser(), target_path), 
                     output_log_level=logging.DEBUG, stdout=None)
    extract_targz(HOMEBREW_URL, target_path, remove_common_prefix=True)
