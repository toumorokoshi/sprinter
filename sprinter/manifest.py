"""
manifest.py is a utility class to help determine version differences in sprinter apps.

example manifest sections look like:
[NAMESPACE:FEATURE]
version = {{ manifest_version }}
"""

import ConfigParser

class Manifest(object):
    """ Class to represent a manifest object """

    def __init__(self, target_manifest_path, source_manifest_path=None):
        """
        If a manifest already exuists, it should be passed in as the source manifest.
        target_manifest_path is the path to the desired manifest file.
        """
