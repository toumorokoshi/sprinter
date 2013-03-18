"""
manifest.py is a utility class to help determine version differences in sprinter apps.

example manifest sections look like:
[FEATURE]
version = {{ manifest_version }}
{{ configuration vars }}
"""

from ConfigParser import RawConfigParser
import logging
import re
import urllib
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
NAMESPACE_REGEX = re.compile('([a-zA-Z0-9_]+)(\.[a-zA-Z0-9_]+)?$')


class ManifestError(Exception):
    pass


class Manifest(RawConfigParser):
    """
    A representation of a manifest object

    a manifest can be one of the following:
    * a string, either a url or a filepath
    * a file-like object

    If the namespace is not passed, it will be pulled from the
    global config object in the target, or assumed from
    the string representation of the target object
    """

    def __init__(self, raw_manifest, namespace=None, logger='sprinter'):
        self.logger = logging.getLogger(logger)
        self._load_manifest(raw_manifest)
        self.namespace = namespace if namespace else self._parse_namespace()

    def source(self):
        """
        Return the manifest source
        """
        return self.get('config', 'source') if \
            self.has_option('config', 'source') else None

    def _load_manifest(self, manifest):
        self.add_section('config')
        if type(manifest) == str:
            if manifest.startswith("http"):
                manifest_file_handler = StringIO(urllib.urlopen(manifest).read())
                self.readfp(manifest_file_handler)
            else:
                self.read(manifest)
            self.set('config', 'source', str(manifest))
        else:
            self.readfp(manifest)

    def _parse_namespace(self):
        """
        Parse the namespace from various sources
        """
        if self.has_option('config', 'namespace'):
            return self.get('config', 'namespace')
        elif self.has_option('config', 'source'):
            return NAMESPACE_REGEX.search(self.get('config', 'source')).groups()[0]
        else:
            self.logger.error('Could not parse namespace implicitely!')
            return None

    def recipe_sections(self):
        """
        Return all sections related to a recipe.
        """
        return [s for s in self.sections() if s != "config"]

    def valid(self):
        """
        Validate the configuration, ensure that the configuration is
        properly formatted.
        """
        return True


class Config(object):
    """
    Class to reconcile manifests

    >>> m.namespace
    'sprinter'
    """

    #source_dict = {}  # source is manipulated as dict until deserialized as a config file
    #target_dict = {}  # target is manipulated as dict until deserialized as a config file
    # a list of values to not save into the config.
    # e.g. passwords
    temporary_sections = []
    config = {}

    def __init__(self, source=None, target=None, namespace=None):
        """
        Takes in a source and target Manifest object, with a namespace
        to override if it is desired.
        """
        self.source = source
        self.target = target
        if not namespace:
            if target and target.namespace:
                self.namespace = target.namespace
            elif source and source.namespace:
                self.namespace = source.namespace
        else:
            self.namespace = namespace

    def grab_inputs(self):
        """
        Look for any inputs not already asked accounted for, and
        query the user for them.
        """
        for s in self.target.recipe_sections():
            if self.target.has_option(s, 'inputs'):
                for param, attributes in \
                        self.__parse_input_string(self.target.get(s, 'inputs')):
                    default = (attributes['default'] if 'default' in attributes else None)
                    secret = (attributes['secret'] if 'secret' in attributes else False)
                    self.get_config(param, default=default, secret=secret)

    def setups(self):
        """
        Return a dictionary with all the features that need to be setup.
        >>> m.setups()
        {'myrc': {'target': {'recipe': 'sprinter.recipes.template'}}}
        """
        new_sections = {}
        for s in self.target.recipe_sections():
            if not self.source or self.source.has_section(s):
                new_sections[s] = {"target": dict(self.target.items(s))}
        return new_sections

    def updates(self):
        """
        Return a dictionary with all the features that need to be
        updated.

        >>> m.updates()
        {'maven': {'source': {'recipe': 'sprinter.recipes.unpack', 'specific_version': '2.10'}, 'target': {'recipe': 'sprinter.recipes.unpack', 'specific_version': '3.0.4'}}}

        >>> old_manifest.updates()
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
        ManifestError: Update method requires a target manifest!
        """
        if not self.target:
            raise ManifestError("Update method requires a target manifest!")
        different_sections = {}
        for s in self.target.recipe_sections():
            if self.source.has_section(s):
                target_dict = dict(self.target.items(s))
                source_dict = dict(self.source.items(s))
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
        for s in self.source.recipe_sections():
            if not self.target or not self.target.has_section(s):
                missing_sections[s] = {"source": dict(self.source.items(s))}
        return missing_sections

    def deactivations(self):
        """
        Return a dictionary of activation recipes.

        >>> m.activations()
        {'maven': {'source': {'recipe': 'sprinter.recipes.unpack', 'specific_version': '2.10'}}, 'ant': {'source': {'recipe': 'sprinter.recipes.unpack', 'specific_version': '1.8.4'}}, 'mysql': {'source': {'brew': 'mysql', 'apt-get': 'libmysqlclient\\nlibmysqlclient-dev', 'recipe': 'sprinter.recipes.package'}}}
        """
        deactivation_sections = {}
        for s in self.source.recipe_sections():
            deactivation_sections[s] = {"source": dict(self.source.items(s))}
        return deactivation_sections

    def activations(self):
        """
        Return a dictionary of activation recipes.

        >>> m.activations()
        {'maven': {'source': {'recipe': 'sprinter.recipes.unpack', 'specific_version': '2.10'}}, 'ant': {'source': {'recipe': 'sprinter.recipes.unpack', 'specific_version': '1.8.4'}}, 'mysql': {'source': {'brew': 'mysql', 'apt-get': 'libmysqlclient\\nlibmysqlclient-dev', 'recipe': 'sprinter.recipes.package'}}}
        """
        activation_sections = {}
        for s in self.source.recipe_sections():
            activation_sections[s] = {"source": dict(self.source.items(s))}
        return activation_sections

    def reloads(self):
        """
        return reload dictionaries
        >>> m.reloads()
        {'maven': {'source': {'recipe': 'sprinter.recipes.unpack', 'specific_version': '2.10'}}, 'ant': {'source': {'recipe': 'sprinter.recipes.unpack', 'specific_version': '1.8.4'}}, 'mysql': {'source': {'brew': 'mysql', 'apt-get': 'libmysqlclient\\nlibmysqlclient-dev', 'recipe': 'sprinter.recipes.package'}}}
        """
        reload_sections = {}
        for s in self.source.recipe_sections():
                reload_sections[s] = {"source": dict(self.source.items(s))}
        return reload_sections

    def write(self, file_handle):
        """
        write the current state to a file manifest
        """
        if not self.target:
            self.target = self.source
        if not self.target.has_section('config'):
            self.target.add_section('config')
        for k, v in self.config.items():
            if k not in self.temporary_sections:
                self.target.set('config', k, v)
        self.target.set('config', 'namespace', self.namespace)
        self.target.write(file_handle)

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
        for s in self.target.sections():
            for k, v in self.target.items(s):
                context_dict["%s:%s" % (s, k)] = v
        for k, v in self.config.items():
                context_dict["config:%s" % k] = v
        return context_dict

    def __detect_namespace(self, manifest_object):
        """
        Find a manifest object
        """
        namespace = ""
        if self.target and self.target.has_section('config') and \
                self.target.has_option('config', 'namespace'):
                namespace = self.target.get('config', 'namespace')
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

    def _create_config_dict(config):
        """
        Convert a ConfigParser to a config_dictionary object
        >>> config = ConfigParser.RawConfigParser()
        >>> config.readfp(StringIO(test_old_version))
        >>> m._config_to_dict(config)
        {}
        """
        pass

if __name__ == '__main__':
    import doctest
    old_manifest = Manifest(StringIO(test_old_version))
    new_manifest = Manifest(StringIO(test_new_version))
    config = Config(source=old_manifest, target=new_manifest)
    doctest.testmod(extraglobs={'c': config,
                                'new_manifest': new_manifest,
                                'old_manifest': old_manifest})
