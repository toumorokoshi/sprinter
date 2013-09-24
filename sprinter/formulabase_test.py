from __future__ import unicode_literals
from mock import Mock, patch
from sprinter.testtools import FormulaTest
from sprinter.formulabase import FormulaBase
import sprinter.lib as lib

source_config = """
"""

target_config = """
[install_with_rc]
formula = sprinter.formulabase
rc = teststring

[install_with_command]
formula = sprinter.formulabase
command = echo 'helloworld'

[osx]
systems = osx
formula = sprinter.formulabase

[osx2]
systems = OsX
formula = sprinter.formulabase

[debian]
systems = debian
formula = sprinter.formulabase
"""


class TestFormulaBase(FormulaTest):
    """ Tests for the formula base """

    def setup(self):
        super(TestFormulaBase, self).setup(source_config=source_config,
                                           target_config=target_config)

    @patch.object(lib, 'call')
    def test_install_with_rc(self, call):
        """ Test install with rc """
        self.environment.run_feature("install_with_rc", 'sync')
        self.directory.add_to_rc.assert_called_once_with('teststring')
        call.called, "lib call was called when it was not specified"

    @patch.object(lib, 'call')
    def test_install_with_command(self, call):
        """ Test install with command """
        self.environment.run_feature("install_with_command", 'sync')
        call.assert_called_once_with("echo 'helloworld'", cwd="/tmp/", shell=True)
        assert not self.directory.add_to_rc.called, "add to rc called when rc not enabled!"

    def test_osx_only(self):
        """ Test a feature that should only occur on osx """
        fb = FormulaBase(self.environment, 'osx',
                         target=self.environment.target.get_feature_config('osx'))
        fb2 = FormulaBase(self.environment, 'osx2',
                          target=self.environment.target.get_feature_config('osx2'))
        self.system.isOSX = Mock(return_value=True)
        assert fb.should_run()
        assert fb2.should_run()
        self.system.isOSX = Mock(return_value=False)
        assert not fb.should_run()
        assert not fb2.should_run()

    def test_debianbased_only(self):
        """ Test a feature that should only occur on debian-based distributions """
        fb = FormulaBase(self.environment, 'debian',
                         target=self.environment.target.get_feature_config('debian'))
        self.system.isDebianBased = Mock(return_value=True)
        assert fb.should_run()
        self.system.isDebianBased = Mock(return_value=False)
        assert not fb.should_run()
