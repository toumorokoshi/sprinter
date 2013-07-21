from mock import Mock, call
from sprinter.testtools import create_mock_environment
from sprinter.exceptions import SprinterException

source_config = """
[config]
test = hi
"""

target_config = """
[config]
inputs = password?
         main_branch?==comp_main

[noformula]
blank = thishasnoformula
"""


class TestEnvironment(object):
    """ Tests for the environment """

    def test_grab_inputs_existing_source(self):
        """ Grabbing inputs should source from source first, if it exists """
        self.environment = create_mock_environment(
            source_config=source_config,
            target_config=target_config
        )
        self.environment.target.get_config = Mock()
        self.environment.grab_inputs()
        self.environment.target.get_config.assert_has_calls([
            call("password", default=None, secret=True, force_prompt=False),
            call("main_branch", default="comp_main", secret=True, force_prompt=False)
        ])
        assert self.environment.target.get_config.call_count == 2, "More calls were called!"

    def test_running_missing_formula(self):
        """ When a formula is missing, a sprinter exception should be thrown at the end """
        self.environment = create_mock_environment(
            target_config=missing_formula_config)
        try:
            self.environment.install()
            raise Exception("Exception not raised!")
        except SprinterException:
            pass


missing_formula_config = """
[missingformula]

[otherformula]
formula = sprinter.formulabase
"""
