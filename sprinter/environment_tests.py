import httpretty
from mock import patch, Mock, call
from sprinter.testtools import FormulaTest
from sprinter import lib

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


class TestEnvironment(FormulaTest):
    """ Tests for the environment """

    def setup(self):
        super(TestEnvironment, self).setup(source_config=source_config,
                                           target_config=target_config)

    def test_grab_inputs_existing_source(self):
        """ Grabbing inputs should source from source first, if it exists """
        self.environment.target.get_config = Mock()
        self.environment.grab_inputs()
        self.environment.target.get_config.assert_has_calls([
            call("password", default=None, secret=True, force_prompt=False),
            call("main_branch", default="comp_main", secret=True, force_prompt=False)
        ])
        assert self.environment.target.get_config.call_count == 2, "More calls were called!"
