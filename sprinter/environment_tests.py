from mock import Mock, call
from nose import tools
from sprinter.testtools import create_mock_environment
from sprinter.exceptions import SprinterException
from sprinter.formulabase import FormulaBase

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

    def test_catch_exception_in_feature(self):
        """
        If an exception occurs in a feature, it should be caught
        and still allow other features to run
        """

    def test_feature_run_order_install(self):
        """ A feature install should have it's methods run in the proper order """
        environment = create_mock_environment(
            target_config=test_target
        )
        mock_formulabase = Mock(spec=FormulaBase)
        mock_formulabase.resolve.return_value = None
        mock_formulabase.validate.return_value = None
        mock_formulabase.prompt.return_value = None
        mock_formulabase.sync.return_value = None
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=mock_formulabase)
        environment.install()
        tools.eq_(mock_formulabase.method_calls, [call.should_run(),
                                                  call.validate(),
                                                  call.resolve(),
                                                  call.prompt(),
                                                  call.sync()])

    def test_feature_run_order_update(self):
        """ A feature update should have it's methods run in the proper order """
        environment = create_mock_environment(
            source_config=test_source,
            target_config=test_target,
            installed=True
        )
        mock_formulabase = Mock(spec=FormulaBase)
        mock_formulabase.resolve.return_value = None
        mock_formulabase.validate.return_value = None
        mock_formulabase.prompt.return_value = None
        mock_formulabase.sync.return_value = None
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=mock_formulabase)
        environment.update()
        tools.eq_(mock_formulabase.method_calls, [call.should_run(),
                                                  call.validate(),
                                                  call.resolve(),
                                                  call.prompt(),
                                                  call.sync()])

    def test_feature_run_order_remove(self):
        """ A feature remove should have it's methods run in the proper order """
        environment = create_mock_environment(
            source_config=test_source,
            installed=True
        )
        mock_formulabase = Mock(spec=FormulaBase)
        mock_formulabase.resolve.return_value = None
        mock_formulabase.validate.return_value = None
        mock_formulabase.prompt.return_value = None
        mock_formulabase.sync.return_value = None
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=mock_formulabase)
        environment.remove()
        tools.eq_(mock_formulabase.method_calls, [call.should_run(),
                                                  call.validate(),
                                                  call.resolve(),
                                                  call.prompt(),
                                                  call.sync()])

    def test_feature_run_order_deactivate(self):
        """ A feature deactivate should have it's methods run in the proper order """
        environment = create_mock_environment(
            source_config=test_source,
            installed=True
        )
        mock_formulabase = Mock(spec=FormulaBase)
        mock_formulabase.resolve.return_value = None
        mock_formulabase.validate.return_value = None
        mock_formulabase.prompt.return_value = None
        mock_formulabase.deactivate.return_value = None
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=mock_formulabase)
        environment.deactivate()
        tools.eq_(mock_formulabase.method_calls, [call.should_run(),
                                                  call.validate(),
                                                  call.resolve(),
                                                  call.prompt(),
                                                  call.deactivate()])

    def test_feature_run_order_activate(self):
        """ A feature should have it's methods run in the proper order """
        environment = create_mock_environment(
            source_config=test_source,
            installed=True
        )
        mock_formulabase = Mock(spec=FormulaBase)
        mock_formulabase.resolve.return_value = None
        mock_formulabase.validate.return_value = None
        mock_formulabase.prompt.return_value = None
        mock_formulabase.activate.return_value = None
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=mock_formulabase)
        environment.activate()
        tools.eq_(mock_formulabase.method_calls, [call.should_run(),
                                                  call.validate(),
                                                  call.resolve(),
                                                  call.prompt(),
                                                  call.activate()])


missing_formula_config = """
[missingformula]

[otherformula]
formula = sprinter.formulabase
"""

test_source = """
[testfeature]
formula = sprinter.formulabase
"""

test_target = """
[testfeature]
formula = sprinter.formulabase
"""
