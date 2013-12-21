from __future__ import unicode_literals
import sprinter.lib as lib
from mock import Mock, patch
from sprinter.testtools import FormulaTest
from sprinter.formula.base import FormulaBase

source_config = """
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
