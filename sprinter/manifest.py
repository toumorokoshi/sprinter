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

[mysql]
recipe = sprinter.recipes.package
version = 4
apt-get = libmysqlclient
          libmysqlclient-dev
brew = mysql
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

[myrc]
recipe = sprinter.recipes.template
version = 1
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

    def setups(self):
        """
        Return a dictionary with all the features that need to be setup.
        >>> m.setups()
        {'myrc': {'target': {'version': '1', 'recipe': 'sprinter.recipes.template'}}}
        """
        new_sections = {}
        for s in self.target_manifest.sections():
            if not self.source_manifest.has_section(s):
                new_sections[s] = {"target": dict(self.target_manifest.items(s))}
        return new_sections

    def updates(self):
        """
        Return a dictionary with all the features that need to be
        updated.
        >>> m.updates()
        {'maven': {'source': {'version': '2', 'recipe': 'sprinter.recipes.unpack', 'specific_version': '2.10'}, 'target': {'version': '3', 'recipe': 'sprinter.recipes.unpack', 'specific_version': '3.0.4'}}}
        """
        different_sections = {}
        for s in self.target_manifest.sections():
            if self.source_manifest.has_section(s):
                target_version = self.target_manifest.get(s, 'version')
                source_version = self.source_manifest.get(s, 'version')
                if target_version != source_version:
                    different_sections[s] = {"source": dict(self.source_manifest.items(s)),
                                             "target": dict(self.target_manifest.items(s))}
        return different_sections

    def destroys(self):
        """
        Return a dictionary with all the features that need to be
        destroyed.
        >>> m.destroys()
        {'mysql': {'source': {'brew': 'mysql', 'apt-get': 'libmysqlclient\\nlibmysqlclient-dev', 'version': '4', 'recipe': 'sprinter.recipes.package'}}}
        """
        missing_sections = {}
        for s in self.source_manifest.sections():
            if not self.target_manifest.has_section(s):
                missing_sections[s] = {"source": dict(self.source_manifest.items(s))}
        return missing_sections


if __name__ == '__main__':
    import doctest
    from StringIO import StringIO
    doctest.testmod(extraglobs={'m': Manifest(StringIO(test_new_version), StringIO(test_old_version))})
