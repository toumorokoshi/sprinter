import httpretty
from sprinter.environment import populate_formula_instance

"""
[noformula]
blank = thishasnoformula
"""


class TestEnvironmentDecorators(object):
    """ Tests for the environment decorators """

    def skip_grab_inputs_existing_source(self):
        """ Grabbing inputs should source from source first, if it exists """
        source_manifest = Manifest(StringIO(manifest_input_params))
        config = Config(source=source_manifest,
                        target=self.new_manifest)
        config.get_config = Mock()
        config.grab_inputs()
        config.get_config.assert_has_calls([
            call("password", default=None, secret=True, force_prompt=False),
            call("main_branch", default="comp_main", secret=True, force_prompt=False)
        ])
        assert config.get_config.call_count == 2, "More calls were called!"

    def skip_grab_inputs_source(self):
        """ Test grabbing inputs from source """
        self.config_source_only.get_config = Mock(return_value="no")
        self.config_source_only.grab_inputs()
        self.config_source_only.get_config.assert_called_once_with(
            "sourceonly", default=None, secret=False, force_prompt=False)
