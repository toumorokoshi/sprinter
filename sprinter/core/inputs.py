from sprinter import lib

INPUT_EMPTY_VALUE = object()


class InputException(Exception):
    pass


class Inputs(object):
    """" A class to handle user input """
    
    def __init__(self):
        self._secret_values = set()  # secret values are not written on save
        self._inputs = set()  # a list of valid inputs to retrieve values from
        self._defaults = {}  # a dictionary of defaults to use
        self._values = {}  # dictionary to store values in

    def add_input(self, key, value=INPUT_EMPTY_VALUE, default=INPUT_EMPTY_VALUE, is_secret=False):
        """ Add an input <input> with a possible <value>, and <is_secret>"""
        self._inputs.add(key)
        if is_secret:
            self._secret_values.add(key)
        if value is not INPUT_EMPTY_VALUE:
            self._values[key] = value
        if default is not INPUT_EMPTY_VALUE:
            self._defaults[key] = default

    def is_input(self, key):
        """ Returns true if <key> is a key """
        return key in self._inputs

    def is_set(self, key):
        if key not in self._inputs:
            raise InputException("Key {0} is not a valid input!".format(key))
        return key in self._values

    def set_input(self, key, value):
        """ Sets the <key> to <value> """
        if key not in self._inputs:
            raise InputException("Key {0} is not a valid input!".format(key))
        self._values[key] = value

    def get_input(self, key, force=False):
        """ Get the value of <key> if it already exists, or prompt for it if not """
        if key not in self._inputs:
            raise InputException("Key {0} is not a valid input!".format(key))
        if key not in self._values or force:
            self._values[key] = lib.prompt("please enter your %s" % key,
                                           default=(self._values.get(key, None) or self._defaults.get(key, None)),
                                           secret=(key in self._secret_values))
        return self._values[key]

    def get_unset_inputs(self):
        """ Return a set of unset inputs """
        return set([k for k in self._inputs if k not in self._values])

    def prompt_unset_inputs(self, force=False):
        """ Prompt for unset input values """
        if force:
            for s in self._inputs:
                self.get_input(s, force=True)
        else:
            for s in self.get_unset_inputs():
                self.get_input(s, force=force)

    def keys(self):
        """ Return a set of valid keys """
        return self._inputs

    def values(self, with_defaults=True):
        """ Return the values dictionary, defaulting to default values """
        return_dict = {}
        for k in self._inputs:
            if k in self._values:
                return_dict[k] = self._values[k]
            elif k in self._defaults:
                return_dict[k] = self._defaults[k]
        return return_dict

    def write_values(self):
        """ Return the dictionary with which to write values """
        return dict(((k, v) for k, v in self.values().items() if k not in self._secret_values))

    def add_inputs_from_inputstring(self, input_string):
        """
        Add inputs using the input string format:

        gitroot==~/workspace
        username
        password?
        main_branch==comp_main
        """
        raw_params = input_string.split('\n')
        param_attributes = (self._parse_param_line(rp) for rp in raw_params if len(rp.strip(' \t')) > 0)
        for param, attributes in param_attributes:
            self.add_input(param,
                           default=attributes.get('default', INPUT_EMPTY_VALUE),
                           is_secret=attributes.get('secret', False))

    def _parse_param_line(self, line):
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
