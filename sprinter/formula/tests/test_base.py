from __future__ import unicode_literals
import sprinter.lib as lib
from mock import Mock, patch
from sprinter.testtools import FormulaTest
from sprinter.formula.base import FormulaBase

source_config = """
[prompt_value_source]
formula = sprinter.formula.base
source_value = old
"""

target_config = """
[install_with_rc]
formula = sprinter.formula.base
rc = teststring

[install_with_command]
formula = sprinter.formula.base
command = echo 'helloworld'

[osx]
systems = osx
formula = sprinter.formula.base

[osx2]
systems = OsX
formula = sprinter.formula.base

[debian]
systems = debian
formula = sprinter.formula.base

[prompt_value]
formula = sprinter.formula.base
existing_value = here

[prompt_value_source]
formula = sprinter.formula.base
"""


class TestFormulaBase(FormulaTest):
    """ Tests for the formula base """

    def setup(self):
        super(TestFormulaBase, self).setup(source_config=source_config,
                                           target_config=target_config)

    def test_install_with_rc(self):
        """ Test install with rc """
        self.directory.add_to_rc = Mock()
        self.environment.run_feature("install_with_rc", 'sync')
        self.directory.add_to_rc.assert_called_once_with('teststring')

    @patch.object(lib, 'call')
    def test_install_with_command(self, call):
        """ Test install with command """
        self.environment.run_feature("install_with_command", 'sync')
        call.assert_called_once_with("echo 'helloworld'", cwd=None, shell=True)

    def test_osx_only(self):
        """ Test a feature that should only occur on osx """
        fb = FormulaBase(self.environment, 'osx',
                         target=self.environment.target.get_feature_config('osx'))
        fb2 = FormulaBase(self.environment, 'osx2',
                          target=self.environment.target.get_feature_config('osx2'))
        with patch('sprinter.lib.system.is_osx') as is_osx:
            is_osx.return_value = True
            assert fb.should_run()
            assert fb2.should_run()
            is_osx.return_value = False
            assert not fb.should_run()
            assert not fb2.should_run()

    def test_debianbased_only(self):
        """ Test a feature that should only occur on debian-based distributions """
        fb = FormulaBase(self.environment, 'debian',
                         target=self.environment.target.get_feature_config('debian'))
        with patch('sprinter.lib.system.is_debian') as is_debian:
            is_debian.return_value = True
            assert fb.should_run()
            is_debian.return_value = False
            assert not fb.should_run()

    def test_prompt_value(self):
        """ _prompt_value should prompt a value if it does not exist in the target """
        fb = FormulaBase(self.environment, 'prompt_value',
                         target=self.environment.target.get_feature_config('prompt_value'))
        with patch('sprinter.lib.prompt') as prompt:
            prompt.return_value = "foo"
            fb._prompt_value('existing_value', 'this value exists')
            assert fb.target.get('existing_value') == "here"
            fb._prompt_value('non_existing_value', "this value doesn't exists")
            assert fb.target.get('non_existing_value') == "foo"

    def test_prompt_value_default(self):
        """ _prompt_value default should be overwritten by the source if it exists """
        fb = FormulaBase(self.environment, 'prompt_value',
                         source=self.environment.source.get_feature_config('prompt_value_source'),
                         target=self.environment.target.get_feature_config('prompt_value_source'))
        with patch('sprinter.lib.prompt') as prompt:
            prompt.return_value = "foo"
            fb._prompt_value('source_value', 'this value exists')
            prompt.assert_called_once_with('this value exists', default="old")
