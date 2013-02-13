"""
manifest.py is a utility class to help determine version differences in sprinter apps.

example manifest sections look like:
[FEATURE]
version = {{ manifest_version }}
{{ configuration vars }}
"""

import ConfigParser

test_old_version = """
[maven]
recipe = sprinter.recipes.unpack
version = 2
specific_version = 2.10

[ant]
recipe = sprinter.recipes.unpack
version = 5
specific_version = 1.8.4
"""

test_new_version = """
[maven]
recipe = sprinter.recipes.unpack
version = 3
specific_version = 3.0.4

[ant]
recipe = sprinter.recipes.unpack
version = 5
specific_version = 1.8.4
"""


class Manifest(object):
    """ Class to represent a manifest object """

    source_manifest = ConfigParser.ConfigParser()
    target_manifest = ConfigParser.ConfigParser()

    def __init__(self, target_manifest, source_manifest=None):
        """
        If a manifest already exists, it should be passed in as the source manifest.
        target_manifest_path is the path to the desired manifest file.
        """
        if type(target_manifest) == str:
            self.target_manifest.read(target_manifest)
        else:
            self.target_manifest.readfp(target_manifest)
        if source_manifest:
            if type(source_manifest) == str:
                self.source_manifest.read(source_manifest)
            else:
                self.source_manifest.readfp(source_manifest)

    def diff(self):
        """
        Return a dictionary with all the features that need to be
        updated.
        >>> m.diff()
        {'maven': {'target': {'version': '3', 'recipe': 'sprinter.recipes.unpack', 'specific_version': '3.0.4'}}}
        """
        different_sections = {}
        for s in self.target_manifest.sections():
            target_version = self.target_manifest.get(s, 'version')
            source_version = (self.source_manifest.get(s, 'version') if
                self.source_manifest.has_section(s) else 0)
            if target_version != source_version:
                different_sections[s] = {"target": dict(self.target_manifest.items(s))}
        return different_sections

if __name__ == '__main__':
    import doctest
    from StringIO import StringIO
    doctest.testmod(extraglobs={'m': Manifest(StringIO(test_new_version), StringIO(test_old_version))})
