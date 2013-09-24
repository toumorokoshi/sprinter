import copy
import sys

from sprinter.core import LOGGER
import sprinter.lib as lib


class ParamNotFoundException(Exception):
    """ Exception for a parameter not being found """


class FeatureConfig(object):

    manifest = None  # the manifest the featureconfig is derived from

    def __init__(self, manifest, feature_name, logger=LOGGER):
        self.feature_name = feature_name
        self.manifest = manifest
        self.raw_dict = dict(manifest.items(feature_name))
        self.logger = logger

    def get(self, param, default=None):
        """
        Returns the param value, and returns the default if it doesn't exist.
        If default is none, an exception will be raised instead.
        
        the returned parameter will have been specialized against the global context
        """
        if not self.has(param):
            if default is not None:
                return default
            raise ParamNotFoundException("value for %s not found" % param)
        context_dict = copy.deepcopy(self.manifest.get_context_dict())
        for k, v in self.raw_dict.items():
            context_dict["%s:%s" % (self.feature_name, k)] = v
        try:
            return str(self.raw_dict[param]) % context_dict
        except KeyError:
            e = sys.exc_info()[1]
            self.logger.warn("Could not specialize %s! Error: %s" % (self.raw_dict[param], e))
            return self.raw_dict[param]

    def has(self, param):
        """ return true if the param exists """
        return param in self.raw_dict

    def set(self, param, value):
        """ sets the param to the value provided """
        self.raw_dict[param] = value
        self.manifest.set(self.feature_name, param, value)

    def remove(self, param):
        """ Remove a parameter from the manifest """
        if self.has(param):
            del(self.raw_dict[param])
            self.manifest.remove_option(self.feature_name, param)

    def keys(self):
        """ return all of the keys in the config """
        return self.raw_dict.keys()

    def is_affirmative(self, param, default=None):
        return lib.is_affirmative(self.get(param, default=default))

    def prompt(self, param, message, default=None, only_if_empty=False):
        """ Prompts the user for a value, passing a default if it exists """
        if self.has(param) and only_if_empty:
            return
        value = lib.prompt(message, default=default)
        self.set(param, value)

    def set_if_empty(self, param, default):
        """ Set the parameter to the default if it doesn't exist """
        if not self.has(param):
            self.set(param, defaulct)
            
    def to_dict(self):
        """ Returns the context, fully specialized, as a dictionary """
        return dict((k, str(self.get(k))) for k in self.raw_dict)

    def write_to_manifest(self):
        """ Overwrites the section of the manifest with the featureconfig's value """
        self.manifest.remove_section(self.feature_name)
        self.manifest.add_section(self.feature_name)
        for k, v in self.raw_dict.items():
            self.manifest.set(self.feature_name, k, v)

    # implementing a dictionary-like behaviour for backwards compatability
    # it's most likely better to use set and get instead
    def __getitem__(self, key):
        try:
            return self.get(key)
        except ParamNotFoundException:
            e = sys.exc_info()[1]
            raise KeyError(str(e))
        
    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key, value):
        self.remove(key, value)

    def __contains__(self, item):
        return self.has(item)

    def __iter__(self):
        return self.raw_dict.__iter__()
