"""
manifest.py is a utility class to help determine version differences in sprinter apps.

example manifest sections look like:
[FEATURE]
version = {{ manifest_version }}
{{ configuration vars }}
"""

import ConfigParser
import urllib
from getpass import getpass
from StringIO import StringIO
from sprinter import lib

test_old_version = """
[config]
namespace = sprinter

[maven]
recipe = sprinter.recipes.unpack
specific_version = 2.10

[ant]
recipe = sprinter.recipes.unpack
specific_version = 1.8.4

[mysql]
recipe = sprinter.recipes.package
apt-get = libmysqlclient
          libmysqlclient-dev
brew = mysql
"""

test_new_version = """
[config]
namespace = sprinter

[maven]
recipe = sprinter.recipes.unpack
specific_version = 3.0.4

[ant]
recipe = sprinter.recipes.unpack
specific_version = 1.8.4

[myrc]
recipe = sprinter.recipes.template
"""

test_input_string = \
"""
gitroot==~/workspace
username
password?
main_branch==comp_main
"""


CONFIG_RESERVED = ['source', 'inputs']


class ManifestError(Exception):
    pass


class Manifest(object):
    """ Class to represent a manifest object

    >>> m.namespace
    'sprinter'
    """

    source_manifest = ConfigParser.RawConfigParser()
    target_manifest = None
    # a list of values to not save into the config.
    # e.g. passwords
    temporary_sections = []
    config = {}

    def __init__(self, target_manifest=None, source_manifest=None, namespace=None):
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
        if target_manifest:
            self.load_target(target_manifest)
        if source_manifest:
            self.load_source(source_manifest)
        if not namespace:
            namespace = self.__detect_namespace(target_manifest)
        self.namespace = namespace

    def load_target(self, target_manifest):
        """ reload the source manifest """
        self.target_manifest = self.__load_manifest(target_manifest)

    def load_target_implicit(self):
        """
        Attempt an implicit load of a target file. An implicit load
        involves looking at source manifest's config:source parameter
        and attempting to load from there. If that's not possible,
        false is returned.
        """
        if self.source_manifest.has_section('config') and \
                self.source_manifest.has_option('config', 'source'):
            self.load_target(self.source_manifest.get('config', 'source'))
            return True
        return False

    def load_source(self, source_manifest):
        """ reload the source manifest """
        self.source_manifest = self.__load_manifest(source_manifest)

    def grab_inputs(self):
        """
        Look for any inputs not already asked accounted for, and
        query the user for them.
        """
        for s in self.target_manifest.sections():
            if self.target_manifest.has_option(s, 'inputs'):
                for param, attributes in \
                        self.__parse_input_string(self.target_manifest.get(s, 'inputs')):
                    default = (attributes['default'] if 'default' in attributes else None)
                    secret = (attributes['secret'] if 'secret' in attributes else False)
                    self.get_config(param, default=default, secret=secret)

    def activations(self):
        """
        Return a dictionary of activation recipes.

        >>> m.activations()
        {'myrc': {'target': {'recipe': 'sprinter.recipes.template'}}}
        """
        activation_sections = {}
        for s in self.source_sections():
            activation_sections[s] = {"source": dict(self.source_manifest.items(s))}
        return activation_sections

    def deactivations(self):
        """
        Return a dictionary of activation recipes.

        >>> m.activations()
        {'myrc': {'target': {'recipe': 'sprinter.recipes.template'}}}
        """
        deactivation_sections = {}
        for s in self.source_sections():
            deactivation_sections[s] = {"source": dict(self.source_manifest.items(s))}
        return deactivation_sections

    def setups(self):
        """
        Return a dictionary with all the features that need to be setup.
        >>> m.setups()
        {'myrc': {'target': {'recipe': 'sprinter.recipes.template'}}}
        """
        new_sections = {}
        for s in self.target_sections():
            if not self.source_manifest.has_section(s):
                new_sections[s] = {"target": dict(self.target_manifest.items(s))}
        return new_sections

    def reloads(self):
        """
        return reload dictionaries
        """
        reload_sections = {}
        for s in self.source_sections():
                reload_sections[s] = {"source": dict(self.source_manifest.items(s))}
        return reload_sections

    def updates(self):
        """
        Return a dictionary with all the features that need to be
        updated.

        >>> m.updates()
        {'maven': {'source': {'recipe': 'sprinter.recipes.unpack', 'specific_version': '2.10'}, 'target': {'recipe': 'sprinter.recipes.unpack', 'specific_version': '3.0.4'}}}

        >>> m_old_only.updates()
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
        ManifestError: Update method requires a target manifest!
        """
        if not self.target_manifest:
            raise ManifestError("Update method requires a target manifest!")
        different_sections = {}
        for s in self.target_sections():
            if self.source_manifest.has_section(s):
                target_dict = dict(self.target_manifest.items(s))
                source_dict = dict(self.source_manifest.items(s))
                if self.__update_needed(source_dict, target_dict):
                    different_sections[s] = {"source": source_dict,
                                             "target": target_dict}
        return different_sections

    def destroys(self):
        """
        Return a dictionary with all the features that need to be
        destroyed.
        >>> m.destroys()
        {'mysql': {'source': {'brew': 'mysql', 'apt-get': 'libmysqlclient\\nlibmysqlclient-dev', 'recipe': 'sprinter.recipes.package'}}}
        """
        missing_sections = {}
        for s in self.source_sections():
            if not self.target_manifest or not self.target_manifest.has_section(s):
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
        if not self.target_manifest:
            self.target_manifest = self.source_manifest
        if not self.target_manifest.has_section('config'):
            self.target_manifest.add_section('config')
        for k, v in self.config.items():
            if k not in self.temporary_sections:
                self.target_manifest.set('config', k, v)
        self.target_manifest.set('config', 'namespace', self.namespace)
        self.target_manifest.write(file_handle)

    def get_config(self, param_name, default=None, secret=False):
        """
        grabs a config from the user space; if it doesn't exist, it will prompt for it.
        """
        prompt = "please enter your %s" % param_name
        if default:
            prompt += " (default %s)" % default
        if param_name not in self.config:
            self.config[param_name] = lib.prompt("please enter your %s" % param_name, default=default, secret=secret)
        if secret:
            self.temporary_sections.append(param_name)
        return self.config[param_name]

    def get_context_dict(self):
        """
        return a context dict of the desired state
        """
        context_dict = {}
        for s in self.target_manifest.sections():
            for k, v in self.target_manifest.items(s):
                context_dict["%s:%s" % (s, k)] = v
        for k, v in self.config.items():
                context_dict["config:%s" % k] = v
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

    def __detect_namespace(self, manifest_object):
        """
        Find a manifest object
        """
        namespace = ""
        if self.target_manifest and self.target_manifest.has_section('config') and \
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

    def __update_needed(self, source_dict, target_dict):
        """
        checks if an update is neede if there is a diff between the items provided

        >>> m._Manifest__update_needed({"a": "b", "c": "d"}, {"a": "b", "c": "e"})
        True

        >>> m._Manifest__update_needed({"a": "b"}, {"a": "b", "c": "e"})
        True

        >>> m._Manifest__update_needed({"a": "b", "c": "d"}, {"a": "b"})
        True

        >>> m._Manifest__update_needed({"a": "b", "c": "d", "e": "f"}, {"a": "b", "c": "d", "e": "f"})
        False
        """
        if len(source_dict) != len(target_dict):
            return True
        for k in source_dict:
            if k not in target_dict or source_dict[k] != target_dict[k]:
                return True
        return False

    def __parse_input_string(self, input_string):
        """
        parse an attribute in a given input string format:

        e.g.:

        inputs = gitroot==~/workspace
                 username
                 password?
                 main_branch==comp_main

        >>> m._Manifest__parse_input_string(test_input_string)
        [('gitroot', {'default': '~/workspace'}), ('username', {}), ('password', {'secret': True}), ('main_branch', {'default': 'comp_main'})]
        """
        raw_params = input_string.split('\n')
        return [self.__parse_param_line(rp) for rp in raw_params if len(rp.strip(' \t')) > 0]

    def __parse_param_line(self, line):
        """
        Parse a single param line.

        >>> m._Manifest__parse_param_line("username")
        ('username', {})

        >>> m._Manifest__parse_param_line("password?")
        ('password', {'secret': True})

        >>> m._Manifest__parse_param_line("main_branch==comp_main")
        ('main_branch', {'default': 'comp_main'})

        >>> m._Manifest__parse_param_line("main_branch?==comp_main")
        ('main_branch', {'default': 'comp_main', 'secret': True})

        >>> m._Manifest__parse_param_line("")
        """
        value = line.strip('\n \t')
        if len(value) > 0:
            attribute_dict = {}
            if value.find('==') != -1:
                value, default = line.split('==')
                attribute_dict['default'] = default
            if value.endswith('?'):
                value = value[:-1]
                attribute_dict['secret'] = True
            return (value, attribute_dict)
        return None

    def __load_manifest(self, manifest):
        manifest_config = ConfigParser.RawConfigParser()
        manifest_config.add_section('config')
        if type(manifest) == str:
            if manifest.startswith("http"):
                manifest_file_handler = StringIO(urllib.urlopen(manifest).read())
                manifest_config.readfp(manifest_file_handler)
            else:
                manifest_config.read(manifest)
            manifest_config.set('config', 'source', str(manifest))
        else:
            manifest_config.readfp(target_manifest)
        return manifest_config


if __name__ == '__main__':
    import doctest
    doctest.testmod(extraglobs={
        'm': Manifest(target_manifest=StringIO(test_new_version), source_manifest=StringIO(test_old_version)),
        'm_new_only': Manifest(target_manifest=StringIO(test_new_version)),
        'm_old_only': Manifest(source_manifest=StringIO(test_old_version))})
