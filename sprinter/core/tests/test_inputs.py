from nose import tools
from mock import patch, call
from sprinter.core.inputs import Inputs, Input, InputException
from sprinter import lib


class TestInput(object):

    def test_input_equality(self):
        a = Input()
        a.value = 'hi'
        a.is_secret = True
        b = Input()
        b.value = 'hi'
        b.is_secret = True
        assert a == b


class TestInputs(object):
    """
    Tests for the input class
    """

    def setUp(self):
        self.inputs = Inputs()

    def test_prompt_unset_imputs(self):
        """ Only unset inputs should be prompted with prompt_unset_inputs """
        self.inputs.add_input('key')
        key_with_value = Input()
        key_with_value.value = 'value'
        self.inputs.add_input('key_with_value', key_with_value)
        with patch.object(lib, 'prompt') as prompt:
            prompt.return_value = "yusuke"
            self.inputs.prompt_unset_inputs()
            prompt.assert_called_once_with("please enter your key", default=None, secret=False)

    def test_forced_prompt_unset_imputs(self):
        """ Only all inputs should be prompted with prompt_unset_inputs and force=True """
        self.inputs.add_input('key')
        key_with_value = Input()
        key_with_value.value = 'value'
        self.inputs.add_input('key_with_value', key_with_value)
        with patch.object(lib, 'prompt') as prompt:
            prompt.return_value = "yusuke"
            self.inputs.prompt_unset_inputs(force=True)
            prompt.assert_has_calls([
                call("please enter your key", default=None, secret=False),
                call("please enter your key_with_value", default='value', secret=False),
            ])

    def test_write_values(self):
        """ Only write values should be returned by write_values """
        secret = Input()
        secret.value = 'value'
        secret.is_secret = True
        not_secret = Input()
        not_secret.value = 'not_secret_value'
        self.inputs.add_input('secret_key', secret)
        self.inputs.add_input('not_secret_key', not_secret)
        tools.eq_(self.inputs.write_values(), {
            'not_secret_key': 'not_secret_value'
        })

    def test_parse_param_line_with_dict(self):
        """ parse_param_line should accept a dict to configure itself """
        test_line = "test?==result#{'prompt':'would you like to do something?'}"
        value, config = self.inputs._parse_param_line(test_line)
        assert value == 'test'
        test_config = Input()
        test_config.prompt = 'would you like to do something?'
        test_config.is_secret = True
        test_config.default = 'result'
        assert config == test_config

    @tools.raises(InputException)
    def test_parse_param_line_with_bad_dict(self):
        """ a bad param line should raise an input exception """
        test_line = "test==result?#{'prompt':'would you like to do something?"
        value, attribute_dict = self.inputs._parse_param_line(test_line)
