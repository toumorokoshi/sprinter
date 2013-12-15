from mock import patch
from sprinter.core.globals import create_default_config, _configure_shell


class TestGlobalConfig(object):
    """ Tests for the global logic """

    def setUp(self):
        self.config = create_default_config()

    def test_global_config_prompt(self):
        """ _configure_shell with 0 should turn all shells on """
        self.config.remove_section('shell')
        with patch('sprinter.lib.prompt') as prompt:
            prompt.return_value = "0"
            _configure_shell(self.config)
            for k, v in self.config.items('shell'):
                assert v == 'true'

    def test_global_config_prompt_special_configs(self):
        """ If no global config exists, it should prompt for the values it needs, and create a file """
        self.config.remove_section('shell')
        with patch('sprinter.lib.prompt') as prompt:
            prompt.return_value = "2,3"
            _configure_shell(self.config)
            assert self.config.get('shell', 'bash') == "false"
            assert self.config.get('shell', 'zsh') == "true"
            assert self.config.get('shell', 'gui') == "true"
