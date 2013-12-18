"""
Utility methods for brew
"""
import logging
import os
from sprinter.lib import extract_targz

HOMEBREW_URL = "http://github.com/mxcl/homebrew/tarball/master"

logger = logging.getLogger(__name__)


def install_brew(target_path):
    """ Install brew to the target path """
    if not os.path.exists(target_path):
        try:
            os.makedirs(target_path)
        except OSError:
            logger.warn("Unable to create directory %s for brew." % target_path)
            logger.warn("Skipping...")
            return
    extract_targz(HOMEBREW_URL, target_path, remove_common_prefix=True)
