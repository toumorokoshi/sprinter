from mock import Mock, patch
from sprinter.testtools import FormulaTest
from sprinter import lib

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
formula = sprinter.formulas.template

[osx2]
systems = OsX
formula = sprinter.formulas.template
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

    def test_install_with_command(self):
        """ Test install with rc """
        self.environment.run_feature("install_with_command", 'sync')
        self.lib.call.assert_called_once_with("echo 'helloworld'", cwd="/tmp/", shell=True)
        assert not self.directory.add_to_rc.called, "add to rc called when rc not enabled!"

    def skip_osx_only(self):
        """ Test a feature that should only occur on osx """
        self.environment.system.isOSX = Mock(return_value=True)
        assert test_manifest.run_phase('osx', 'install')
        assert test_manifest.run_phase('osx2', 'install')
        test_manifest.system.isOSX = Mock(return_value=False)
        assert not test_manifest.run_phase('osx', 'install')
        assert not test_manifest.run_phase('osx2', 'install')

    def skip_debianbased_only(self):
        """ Test a feature that should only occur on debian-based distributions """
        test_manifest = Manifest(StringIO(debian_only_manifest))
        test_manifest.system = Mock(spec=System)
        test_manifest.system.isDebianBased = Mock(return_value=True)
        assert test_manifest.run_phase('debian', 'install')
        test_manifest.system.isDebianBased = Mock(return_value=False)
        assert not test_manifest.run_phase('debian', 'install')
        assert not test_manifest.run_phase('debian', 'update')
