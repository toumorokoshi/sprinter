"""
manifest.py is a utility class to help determine version differences in sprinter apps.

example manifest sections look like:
[FEATURE]
version = {{ manifest_version }}
{{ configuration vars }}
"""

import ConfigParser
import urllib

test_old_version = """
[config]
namespace = sprinter

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
[config]
namespace = sprinter

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
    """ Class to represent a manifest object

    >>> m.namespace
    'sprinter'
    """

    source_manifest = ConfigParser.RawConfigParser()
    target_manifest = ConfigParser.RawConfigParser()
    config = {}

    def __init__(self, target_manifest, source_manifest=None, namespace=None):
        """
        If a manifest already exists, it should be passed in as the source manifest.
        target_manifest_path is the path to the desired manifest file.

        a manifest can be one of the following:
        * a string, either a url or a filepath
        * a file-like object

        If the namespace is not passed, it will be pulled from the
        global config object in the target_manifest, or assumed from
        the string representation of the target_manifest object

        """
        self.load_target(target_manifest)
        if source_manifest:
            self.load_source(source_manifest)
        if not namespace:
            namespace = self.__detect_namespace(target_manifest)
        self.namespace = namespace

    def load_target(self, target_manifest):
        """ reload the source manifest """
        if type(target_manifest) == str:
            if target_manifest.startswith("http"):
                self.target_manifest.readfp(urllib.urlopen(target_manifest))
            else:
                self.target_manifest.read(target_manifest)
        else:
            self.target_manifest.readfp(target_manifest)

    def load_source(self, source_manifest):
        """ reload the source manifest """
        if type(source_manifest) == str:
            if source_manifest.startswith("http"):
                self.source_manifest.readfp(urllib.urlopen(source_manifest))
            else:
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
        for s in self.target_sections():
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
        for s in self.target_sections():
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
        for s in self.source_sections():
            if not self.target_manifest.has_section(s):
                missing_sections[s] = {"source": dict(self.source_manifest.items(s))}
        return missing_sections

    def validate(self):
        """
        Checks validity of manifest files.
        """
        pass

    def write(self, file_handle):
        """
        write the current state to a file manifest
        """
        if not self.target_manifest.has_section('config'):
            self.target_manifest.add_section('config')
        self.target_manifest.set('config', 'namespace', self.namespace)
        self.target_manifest.write(file_handle)

    def get_config(self, param_name, default=None):
        """
        grabs a config from the user space; if it doesn't exist, it will prompt for it.
        """
        if param_name not in self.config:
            self.config[param_name] = self.__prompt("please enter your %s" % param_name, default=default)
        return self.config[param_name]

    def get_context_dict(self):
        """
        return a context dict of the desired state
        """
        context_dict = {}
        for s in self.target_manifest.sections():
            for k, v in self.target_manifest.items(s):
                context_dict["%s:%s" % (s, k)] = v
        return context_dict

    def source_sections(self):
        """
        return all source sections except for reserved ones
        """
        return [s for s in self.source_manifest.sections() if s != "config"]

    def target_sections(self):
        """
        return all target sections except for reserved ones
        """
        return [s for s in self.target_manifest.sections() if s != "config"]

    def __prompt(prompt_string, default=None):
        """
        Prompt user for a string, with a default value
        """
        prompt_string += (" (default %s):" % default if default else ":")
        val = raw_input(prompt_string)
        return (val if val else default)

    def __detect_namespace(self, manifest_object):
        """
        Find a manifest object
        """
        namespace = ""
        if self.target_manifest.has_section('config') and \
          self.target_manifest.has_option('config', 'namespace'):
            namespace = self.target_manifest.get('config', 'namespace')
        else:
            s = str(manifest_object)
            if s.endswith(".cfg"):
                s = s[:-4]
            if s.startswith("http"):
                s = s.split("/")[-1]
            namespace = s
        return namespace


if __name__ == '__main__':
    import doctest
    from StringIO import StringIO
    doctest.testmod(extraglobs={'m': Manifest(StringIO(test_new_version), StringIO(test_old_version))})
