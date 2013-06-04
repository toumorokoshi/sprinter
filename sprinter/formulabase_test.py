from mock import Mock
from sprinter.testtools import FormulaTest

source_config = """
"""

target_config = """
[install_with_rc]
formula = sprinter.formulabase
rc = teststring

[install_with_command]
formula = sprinter.formulabase
command = echo 'helloworld'
"""


class TestFormulaBase(FormulaTest):
    """ Tests for the formula base """

    def setup(self):
        super(TestFormulaBase, self).setup(source_config=source_config,
                                           target_config=target_config)

    def test_install_with_rc(self):
        """ Test install with rc """
        self.environment.install_feature("install_with_rc")
        self.directory.add_to_rc.assert_called_once_with('teststring')
        assert not self.lib.call.called, "lib call was called when it was not specified"

    def test_install_with_command(self):
        """ Test install with rc """
        self.environment.install_feature("install_with_command")
        self.lib.call.assert_called_once_with("echo 'helloworld'", cwd="/tmp/", bash=True)
        assert not self.directory.add_to_rc.called, "add to rc called when rc not enabled!"
