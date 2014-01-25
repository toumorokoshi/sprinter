from __future__ import unicode_literals
from sprinter import lib

EMPTY = object()


class InputException(Exception):
    pass


class Input(object):
    """ struct to hold input information """

    value = EMPTY
    default = EMPTY
    is_secret = False
    prompt = None

    def __eq__(self, other):
        for val in ('value', 'default', 'is_secret', 'prompt'):
            a = getattr(self, val, None)
            b = getattr(other, val, None)
            if not (a == b or a is b):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class Inputs(object):
    """" A class to handle user input """

    def __init__(self):
        self._inputs = {}

    def add_input(self, key, input_instance=None):
        """ Add an input <input> with a possible <value>, and <is_secret>"""
        self._inputs[key] = input_instance or Input()

    def is_input(self, key):
        """ Returns true if <key> is a key """
        return key in self._inputs

    def is_set(self, key):
        if key not in self._inputs:
            raise InputException("Key {0} is not a valid input!".format(key))
        return self._inputs[key].value is not EMPTY

    def set_input(self, key, value):
        """ Sets the <key> to <value> """
        if key not in self._inputs:
            raise InputException("Key {0} is not a valid input!".format(key))
        self._inputs[key].value = value

    def get_input(self, key, force=False):
        """ Get the value of <key> if it already exists, or prompt for it if not """
        prompt = "please enter your {0}".format(key)
        if self._inputs[key].prompt:
            prompt = self._inputs[key].prompt
        if key not in self._inputs:
            raise InputException("Key {0} is not a valid input!".format(key))

        if self._inputs[key].value is EMPTY or force:

            default_value = None
            if self._inputs[key].default is not EMPTY:
                default_value = self._inputs[key].default
            if self._inputs[key].value is not EMPTY:
                default_value = self._inputs[key].value

            self._inputs[key].value = lib.prompt(
                prompt,
                default=default_value,
                secret=self._inputs[key].is_secret)

        return self._inputs[key].value

    def get_unset_inputs(self):
        """ Return a set of unset inputs """
        return set([k for k, v in self._inputs.items() if v.value is EMPTY])

    def prompt_unset_inputs(self, force=False):
        """ Prompt for unset input values """
        if force:
            for s in sorted(self._inputs):
                self.get_input(s, force=True)
        else:
            for s in sorted(self.get_unset_inputs()):
                self.get_input(s, force=force)

    def keys(self):
        """ Return a set of valid keys """
        return self._inputs.keys()

    def values(self, with_defaults=True):
        """ Return the values dictionary, defaulting to default values """
        return_dict = {}
        for k, v in self._inputs.items():
            if v.value is not EMPTY:
                return_dict[k] = v.value
            elif with_defaults and v.default is not EMPTY:
                return_dict[k] = v.default
        return return_dict

    def write_values(self):
        """ Return the dictionary with which to write values """
        return dict(((k, v) for k, v in self.values().items() if not self._inputs[k].is_secret))

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
            self.add_input(param, attributes)

    def _parse_param_line(self, line):
        """ Parse a single param line. """
        value = line.strip('\n \t')
        if len(value) > 0:
            i = Input()
            if value.find('#') != -1:
                value, extra_attributes = value.split('#')
                try:
                    extra_attributes = eval(extra_attributes)
                except SyntaxError:
                    raise InputException("Incorrectly formatted input for {0}!".format(value))
                if not isinstance(extra_attributes, dict):
                    raise InputException("Incorrectly formatted input for {0}!".format(value))
                if 'prompt' in extra_attributes:
                    i.prompt = extra_attributes['prompt']
            if value.find('==') != -1:
                value, default = value.split('==')
                i.default = default
            if value.endswith('?'):
                value = value[:-1]
                i.is_secret = True
            return (value, i)
        return None
