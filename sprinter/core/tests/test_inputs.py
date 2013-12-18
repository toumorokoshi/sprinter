from nose import tools
from mock import patch, call
from sprinter.core.inputs import Inputs
from sprinter import lib


class TestInputs(object):
    """
    Tests for the input class
    """

    def setUp(self):
        self.inputs = Inputs()

    def test_prompt_unset_imputs(self):
        """ Only unset inputs should be prompted with prompt_unset_inputs """
        self.inputs.add_input('key')
        self.inputs.add_input('key_with_value', 'value')
        with patch.object(lib, 'prompt') as prompt:
            prompt.return_value = "yusuke"
            self.inputs.prompt_unset_inputs()
            prompt.assert_called_once_with("please enter your key", default=None, secret=False)

    def test_forced_prompt_unset_imputs(self):
        """ Only all inputs should be prompted with prompt_unset_inputs and force=True """
        self.inputs.add_input('key')
        self.inputs.add_input('key_with_value', 'value')
        with patch.object(lib, 'prompt') as prompt:
            prompt.return_value = "yusuke"
            self.inputs.prompt_unset_inputs(force=True)
            prompt.assert_has_calls([
                call("please enter your key_with_value", default='value', secret=False),
                call("please enter your key", default=None, secret=False),
            ])

    def test_write_values(self):
        """ Only write values should be returned by write_values """
        self.inputs.add_input('secret_key', 'value', is_secret=True)
        self.inputs.add_input('not_secret_key', 'not_secret_value')
        tools.eq_(self.inputs.write_values(), {
            'not_secret_key': 'not_secret_value'
        })
