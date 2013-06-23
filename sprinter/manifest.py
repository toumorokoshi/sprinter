"""
manifest.py is a utility class to help determine version differences in sprinter apps.

example manifest sections look like:
[FEATURE]
version = {{ manifest_version }}
{{ configuration vars }}

The manifest can take a source and/or a target manifest
"""

from ConfigParser import RawConfigParser
import logging
import re
import urllib
from StringIO import StringIO

from sprinter import lib
from sprinter.dependencytree import DependencyTree, DependencyTreeException
from sprinter.system import System

CONFIG_RESERVED = ['source', 'inputs']
FEATURE_RESERVED = ['rc', 'command', 'phase']
NAMESPACE_REGEX = re.compile('([a-zA-Z0-9_]+)(\.[a-zA-Z0-9_]+)?$')


class ManifestException(Exception):
    pass


class Manifest(object):
    """
    A representation of a manifest object

    a manifest can be one of the following:
    * a string, either a url or a filepath
    * a file-like object

    If the namespace is not passed, it will be pulled from the
    global config object in the target, or assumed from
    the string representation of the target object
    """
    dtree = None  # dependency tree object to ascertain order
    invalidations = []   # a list of the invalidation of the Manifest. Aggregated while parsing
    additional_context_variables = {}  # a list of the additional context variables available

    def __init__(self, raw_manifest, namespace=None, logger=None,
                 username=None, password=None):
        self.logger = logger if logger else logging.getLogger('sprinter')
        self.manifest = self.__load_manifest(raw_manifest,
                                             username=username,
                                             password=password)
        self.namespace = namespace if namespace else self.__parse_namespace()
        self.dtree = self.__generate_dependency_tree()
        self.system = System(logger=self.logger)

    def source(self):
        """
        Return the manifest source
        """
        return self.get('config', 'source') if \
            self.has_option('config', 'source') else None

    def formula_sections(self):
        """
        Return all sections related to a formula, re-ordered according to the "depends" section.
        """
        if self.dtree is not None:
            return self.dtree.order
        else:
            return [s for s in self.manifest.sections() if s != "config"]

    def is_true(self, section, option):
        """
        Return true if the section option combo exists and it is set
        to a truthy value.
        """
        return self.has_option(section, option) and \
            self.get(section, option).lower().startswith('t')

    def get_feature_class(self, section):
        if section not in self.formula_sections():
            raise ManifestException("Cannot get feature %s!" % section)
        return self.manifest.get(section, 'formula')

    def get_feature_config(self, feature):
        """ Get the feature configuration for a class """
        context_dict = dict(self.additional_context_variables.items() +
                            self.get_context_dict().items())
        return self.__substitute_objects(dict(self.manifest.items(feature)), context_dict)

    def get_context_dict(self):
        """ return a context dict of the desired state """
        context_dict = {}
        for s in self.formula_sections():
            for k, v in self.manifest.items(s):
                context_dict["%s:%s" % (s, k)] = v
        return_dict = dict(context_dict.items() + self.additional_context_variables.items())
        return_dict_escaped = dict([("%s|escaped" % k, re.escape(v or "")) for k, v in return_dict.items()])
        return dict(return_dict.items() + return_dict_escaped.items())

    def run_phase(self, feature, phase_name):
        """ Determine if the feature should run in the given phase """
        should_run = True
        if(self.manifest.has_option(feature, 'phases') and
                phase_name not in [x.strip() for x in self.manifest.get(feature, 'phases').split(",")]):
            return False
        if self.manifest.has_option(feature, 'systems'):
            should_run = False
            valid_systems = [s.lower() for s in self.manifest.get(feature, 'systems').split(",")]
            for system_type, param in [('isOSX', 'osx'),
                                       ('isDebianBased', 'debian')]:
                if param in valid_systems and getattr(self.system, system_type)() is True:
                    should_run = True
        return should_run
                    
    def add_additional_context(self, additonal_context):
        """ Add additional context variable """
        self.additional_context_variables = dict(self.additional_context_variables.items() + additonal_context.items())

    def __load_manifest(self, raw_manifest, username=None, password=None):
        manifest = RawConfigParser()
        manifest.add_section('config')
        if type(raw_manifest) == str:
            if raw_manifest.startswith("http"):
                if username and password:
                    manifest_file_handler = StringIO(lib.authenticated_get(username,
                                                                           password,
                                                                           raw_manifest))
                else:
                    manifest_file_handler = StringIO(urllib.urlopen(raw_manifest).read())
                manifest.readfp(manifest_file_handler)
            else:
                manifest.read(raw_manifest)
            manifest.set('config', 'source', str(raw_manifest))
        elif raw_manifest.__class__ == RawConfigParser:
            return raw_manifest
        else:
            manifest.readfp(raw_manifest)
        return manifest

    def __parse_namespace(self):
        """
        Parse the namespace from various sources
        """
        if self.manifest.has_option('config', 'namespace'):
            return self.manifest.get('config', 'namespace')
        elif self.manifest.has_option('config', 'source'):
            return NAMESPACE_REGEX.search(self.manifest.get('config', 'source')).groups()[0]
        else:
            self.logger.error('Could not parse namespace implicitely!')
            return None

    def __generate_dependency_tree(self):
        """
        Generate the dependency tree object
        """
        dependency_dict = {}
        for s in self.manifest.sections():
            if s != "config":
                if self.manifest.has_option(s, 'depends'):
                    dependency_list = [d.strip() for d in re.split('\n|,', self.manifest.get(s, 'depends'))]
                    dependency_dict[s] = dependency_list
                else:
                    dependency_dict[s] = []
        try:
            return DependencyTree(dependency_dict)
        except DependencyTreeException as dte:
            self.logger.error("Dependency tree for manifest is invalid! %s" % str(dte))
            self.invalidations.append("Issue with building dependency tree: %s" % str(dte))
            return None

    def __substitute_objects(self, value, context_dict):
        """
        recursively substitute value with the context_dict
        """
        if type(value) == dict:
            return dict([(k, self.__substitute_objects(v, context_dict)) for k, v in value.items()])
        elif type(value) == str:
            try:
                return value % context_dict
            except KeyError as e:
                self.logger.warn("Could not specialize %s! Error: %s" % (value, e))
                return value
        else:
            return value

    # custom equality method
    def __eq__(self, other):
        if not isinstance(other, Manifest):
            return False
        for s in self.manifest.sections():
            if s not in other.manifest.sections():
                return False
            for option in self.manifest.options(s):
                if(not other.manifest.has_option(s, option) or
                   self.manifest.get(s, option) != other.manifest.get(s, option)):
                    return False
        return True
                
    # act like a configparser if asking for a non-existent method.
    def __getattr__(self, name):
        return getattr(self.manifest, name)


class ConfigException(Exception):
    """ Specifies exception is with a config """


class Config(object):
    """
    Class to reconcile manifests

    >>> c.namespace
    'sprinter'
    """

    #source_dict = {}  # source is manipulated as dict until deserialized as a config file
    #target_dict = {}  # target is manipulated as dict until deserialized as a config file
    # a list of values to not save into the config.
    # e.g. passwords
    temporary_sections = []
    source_location = None
    config = {}

    def __init__(self, source=None, target=None, namespace=None, lib=lib):
        """
        Takes in a source and target Manifest object, with a namespace
        to override if it is desired.
        """
        self.lib = lib
        self.source = source
        self.target = target
        if self.target:
            self.source_location = self.target.source()
        if self.source and not self.source_location:
            self.source.source()
        # store raws to use on write
        self.source_raw = source
        self.target_raw = target
        if not namespace:
            if target and target.namespace:
                self.namespace = target.namespace
            elif source and source.namespace:
                self.namespace = source.namespace
        else:
            self.namespace = namespace
        if self.source:
            self.__load_configs(self.source)

    def installs(self):
        """ Return a list of the features which need to be installed. """
        if not self.target:
            raise ConfigException("Install method requires a target manifest!")
        return [s for s in self.target.formula_sections()
                if self.target.run_phase(s, "setup")
                if not self.source or not self.source.has_section(s)]

    def updates(self):
        """ Return a list of features which need to be updated. """
        if not self.target:
            raise ConfigException("Update method requires a target manifest!")
        if not self.source:
            raise ConfigException("Update method requires a source manifest!")
        return [s for s in self.target.formula_sections()
                if self.target.run_phase(s, "update")
                if self.source.has_section(s)]

    def removes(self):
        """ Return a list of features which need to be destroyed. """
        if not self.source:
            raise ConfigException("Remove method requires a source manifest!")
        return [s for s in self.source.formula_sections()
                if self.source.run_phase(s, "remove")
                if not self.target or not self.target.has_section(s)]

    def deactivations(self):
        """ Return a list of the features which need to be deactivated. """
        if not self.source:
            raise ConfigException("Deactivations method requires a source manifest!")
        return [s for s in self.source.formula_sections()
                if self.source.run_phase(s, "deactivate")]

    def activations(self):
        """ Return a list of the features which need to be deactivated. """
        if not self.source:
            raise ConfigException("Activations method requires a source manifest!")
        return [s for s in self.source.formula_sections()
                if self.source.run_phase(s, "activate")]

    def grab_inputs(self, manifest=None):
        """
        Look for any inputs not already accounted for in the manifest, and
        query the user for them.
        """
        if not manifest:
            manifest = self.target if self.target else self.source
        old_manifest = self.source if manifest is self.target else None
        if manifest:
            for s in manifest.sections():
                if manifest.has_option(s, 'inputs'):
                    for param, attributes in \
                            self.__parse_input_string(manifest.get(s, 'inputs')):
                        if old_manifest and old_manifest.has_option('config', param):
                            self.config[param] = old_manifest.get('config', param)
                        else:
                            default = (attributes['default'] if 'default' in attributes else None)
                            secret = (attributes['secret'] if 'secret' in attributes else False)
                            self.get_config(param, default=default, secret=secret)
            if self.target:
                self.set_additional_context('target')
            if self.source:
                self.set_additional_context('source')

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
        if self.source_location:
            self.target.set('config', 'source', self.source_location)
        self.target.write(file_handle)

    def get_config(self, param_name, default=None, secret=False):
        """
        grabs a config from the user space; if it doesn't exist, it will prompt for it.
        """
        if param_name not in self.config:
            self.config[param_name] = self.lib.prompt("please enter your %s" % param_name,
                                                      default=default,
                                                      secret=secret)
        if secret:
            self.temporary_sections.append(param_name)
        return self.config[param_name]

    def set_additional_context(self, manifest_type='target', additional_context={}):
        """
        return a context dict of the desired state
        """
        if not hasattr(self, manifest_type):
            raise ConfigException("manifest_type '%s' doesn't exist!" % manifest_type)
        manifest = getattr(self, manifest_type)
        context_dict = manifest.additional_context_variables
        for k, v in self.config.items():
                context_dict["config:%s" % k] = v
        manifest.additional_context_variables = dict(context_dict.items() +
                                                     additional_context.items())

    def __load_configs(self, config):
        if config.has_section('config'):
            for k, v in config.items('config'):
                self.config[k] = v

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

    def __parse_input_string(self, input_string):
        """
        parse an attribute in a given input string format:

        e.g.:

        inputs = gitroot==~/workspace
                 username
                 password?
                 main_branch==comp_main
        """
        raw_params = input_string.split('\n')
        return [self.__parse_param_line(rp) for rp in raw_params if len(rp.strip(' \t')) > 0]

    def __parse_param_line(self, line):
        """ Parse a single param line. """
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

    def context(self, manifest_type=None):
        """ get the context dictionary desired """
        manifest = None
        if manifest_type is None:
            manifest = self.target if self.target else self.source
        else:
            manifest = getattr(self, manifest_type)
        return manifest.get_context_dict()

    def set_source(self, source_manifest):
        """ Set the source manifest """
        self.source = source_manifest
        self.set_additional_context('source')
        return source_manifest
