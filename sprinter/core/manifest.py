"""
manifest.py is a utility class to help determine version differences in sprinter apps.

example manifest sections look like:
[FEATURE]
version = {{ manifest_version }}
{{ configuration vars }}

The manifest can take a source and/or a target manifest
"""
from __future__ import unicode_literals

import logging
import os
import re
import sys
from io import StringIO

from six.moves import configparser
from six import string_types
import requests
import sprinter.lib as lib
from sprinter.lib.compatability import create_configparser
from sprinter.lib.dependencytree import DependencyTree, DependencyTreeException
from .featureconfig import FeatureConfig
from .inputs import Inputs

CONFIG_RESERVED = ['source', 'inputs']
FEATURE_RESERVED = ['rc', 'command', 'phase']
NAMESPACE_REGEX = re.compile('([a-zA-Z0-9_]+)(\.[a-zA-Z0-9_]+)?$')
MANIFEST_NULL_KEY = object()

logger = logging.getLogger(__name__)


def load_manifest(raw_manifest, namespace=None, **kwargs):
    """ wrapper method which generates the manifest from various sources """
    if isinstance(raw_manifest, configparser.RawConfigParser):
        return Manifest(raw_manifest)

    manifest = create_configparser()

    if not manifest.has_section('config'):
        manifest.add_section('config')

    _load_manifest_interpret_source(manifest, 
                                    raw_manifest, 
                                    **kwargs)

    return Manifest(manifest, namespace=namespace)


def _load_manifest_interpret_source(manifest, source, username=None, password=None, verify_certificate=True, do_inherit=True):
    """ Interpret the <source>, and load the results into <manifest> """
    try:
        if isinstance(source, string_types):
            if source.startswith("http"):
                # if manifest is a url
                _load_manifest_from_url(manifest, source,
                                        verify_certificate=verify_certificate,
                                        username=username, password=password)
            else:
                _load_manifest_from_file(manifest, source)
            if not manifest.has_option('config', 'source'):
                manifest.set('config', 'source', str(source))
        else:
            # assume source is a file pointer
            manifest.readfp(source)
        if manifest.has_option('config', 'extends') and do_inherit:
            parent_manifest = configparser.RawConfigParser()
            _load_manifest_interpret_source(parent_manifest, 
                                            manifest.get('config', 'extends'),
                                            username=username,
                                            password=password,
                                            verify_certificate=verify_certificate)
            for s in parent_manifest.sections():
                for k, v in parent_manifest.items(s):
                    if not manifest.has_option(s, k):
                        manifest.set(s, k, v)

    except configparser.Error:
        logger.debug("", exc_info=True)
        error_message = sys.exc_info()[1]
        raise ManifestException("Unable to parse manifest!: {0}".format(error_message))
    

def _load_manifest_from_url(manifest, url, verify_certificate=True, username=None, password=None):
    """ load a url body into a manifest """
    try:
        if username and password:
            manifest_file_handler = StringIO(lib.authenticated_get(username, password, url,
                                                                   verify=verify_certificate).decode("utf-8"))
        else:
            manifest_file_handler = StringIO(lib.cleaned_request('get', url).text)
        manifest.readfp(manifest_file_handler)
    except requests.exceptions.RequestException:
        logger.debug("", exc_info=True)
        error_message = sys.exc_info()[1]
        raise ManifestException("There was an error retrieving {0}!\n {1}".format(url, str(error_message)))


def _load_manifest_from_file(manifest, path):
    """ load manifest from file """
    if not os.path.exists(os.path.expanduser(path)):
        raise ManifestException("Manifest does not exist at {0}!".format(path))
    manifest.read(path)


class ManifestException(Exception):
    """ Returned if an exception occurred with the manifest """


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
    additional_context_variables = {}  # a list of the additional context variables available

    def __init__(self, raw_manifest, namespace=None):
        self.manifest = raw_manifest
        if not self.manifest.has_section('config'):
            self.manifest.add_section('config')
        self.inputs = self.__setup_inputs()
        self.namespace = namespace or self.__parse_namespace()
        self.dtree = self.__generate_dependency_tree()

    def formula_sections(self):
        """
        Return all sections related to a formula, re-ordered according to the "depends" section.
        """
        if self.dtree is not None:
            return self.dtree.order
        else:
            return [s for s in self.manifest.sections() if s != "config"]

    def source(self):
        """
        Return the manifest source
        """
        return self.get('config', 'source') if \
            self.has_option('config', 'source') else None

    def set_source(self, source):
        """ Set the manifest source """
        self.set('config', 'source', source)

    def is_affirmative(self, section, option):
        """
        Return true if the section option combo exists and it is set
        to a truthy value.
        """
        return self.has_option(section, option) and \
            lib.is_affirmative(self.get(section, option))

    def set_input(self, key, value):
        if self.inputs.is_input(key):
            self.inputs.set_input(key, value)
        self.set('config', key, value)
    
    def write(self, file_handle):
        """ write the current state to a file manifest """
        for k, v in self.inputs.write_values().items():
            self.set('config', k, v)
        self.set('config', 'namespace', self.namespace)
        self.manifest.write(file_handle)

    def grab_inputs(self, force=False):
        self.inputs.prompt_unset_inputs(force=force)

    def get_feature_config(self, feature_name):
        """ Return a FeatureConfig for the feature name provided """
        return FeatureConfig(self, feature_name)

    def get_context_dict(self):
        """ return a context dict of the desired state """
        context_dict = {}
        for s in self.sections():
            for k, v in self.manifest.items(s):
                context_dict["%s:%s" % (s, k)] = v
        for k, v in self.inputs.values().items():
            context_dict["config:{0}".format(k)] = v
        context_dict.update(self.additional_context_variables.items())
        context_dict.update(dict([("%s|escaped" % k, re.escape(str(v) or "")) for k, v in context_dict.items()]))
        return context_dict

    def add_additional_context(self, additional_context):
        """ Add additional context variable """
        self.additional_context_variables.update(additional_context)

    def get(self, section, key, default=MANIFEST_NULL_KEY):
        """ Returns the value if it exist, or default if default is set """
        if not self.manifest.has_option(section, key) and default is not MANIFEST_NULL_KEY:
            return default
        return self.manifest.get(section, key)

    def __parse_namespace(self):
        """
        Parse the namespace from various sources
        """
        if self.manifest.has_option('config', 'namespace'):
            return self.manifest.get('config', 'namespace')
        elif self.manifest.has_option('config', 'source'):
            return NAMESPACE_REGEX.search(self.manifest.get('config', 'source')).groups()[0]
        else:
            logger.warn('Could not parse namespace implicitely')
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
        except DependencyTreeException:
            dte = sys.exc_info()[1]
            raise ManifestException("Dependency tree for manifest is invalid! %s" % str(dte))

    def __substitute_objects(self, value, context_dict):
        """
        recursively substitute value with the context_dict
        """
        if type(value) == dict:
            return dict([(k, self.__substitute_objects(v, context_dict)) for k, v in value.items()])
        elif type(value) == str:
            try:
                return value % context_dict
            except KeyError:
                e = sys.exc_info()[1]
                logger.warn("Could not specialize %s! Error: %s" % (value, e))
                return value
        else:
            return value

    def __setup_inputs(self):
        """ Setup the inputs object """
        input_object = Inputs()
        # populate input schemas
        for s in self.manifest.sections():
            if self.has_option(s, 'inputs'):
                input_object.add_inputs_from_inputstring(self.get(s, 'inputs'))
        # add in values
        for k, v in self.items('config'):
            if input_object.is_input(s):
                input_object.set_input(k, v)
        return input_object
        
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
