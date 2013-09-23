from __future__ import unicode_literals
from mock import patch
from sprinter.testtools import FormulaTest
import sprinter.lib as lib

source_config = """
[update]
formula = sprinter.formula.command
update = echo 'this is old...'

[remove]
formula = sprinter.formula.command
remove = echo 'destroy up...'

[deactivate]
formula = sprinter.formula.command
deactivate = echo 'deactivating...'

[activate]
formula = sprinter.formula.command
activate = echo 'activating...'
"""

target_config = """
[install]
formula = sprinter.formula.command
install = echo 'setting up...'
update = echo 'updating...'

[update]
formula = sprinter.formula.command
update = echo 'update up...'

[with-shell]
formula = sprinter.formula.command
install = echo 'installing...'
shell = True
"""


class TestCommandFormula(FormulaTest):
    """
    Tests for the command formula.
    """
    def setup(self):
        super(TestCommandFormula, self).setup(source_config=source_config,
                                              target_config=target_config)

    def teardown(self):
        del(self.environment)

    @patch.object(lib, 'call')
    def test_install(self, call):
        self.environment.run_feature("install", 'sync')
        call.assert_called_once_with("echo 'setting up...'", shell=False)

    @patch.object(lib, 'call')
    def test_update(self, call):
        self.environment.run_feature("update", 'sync')
        call.assert_called_once_with("echo 'update up...'", shell=False)

    @patch.object(lib, 'call')
    def test_remove(self, call):
        self.environment.run_feature("remove", 'sync')
        call.assert_called_once_with("echo 'destroy up...'", shell=False)

    @patch.object(lib, 'call')
    def test_deactivate(self, call):
        self.environment.run_feature("deactivate", 'deactivate')
        call.assert_called_once_with("echo 'deactivating...'", shell=False)

    @patch.object(lib, 'call')
    def test_activate(self, call):
        self.environment.run_feature("activate", 'activate')
        call.assert_called_once_with("echo 'activating...'", shell=False)

    @patch.object(lib, 'is_affirmative')
    @patch.object(lib, 'call')
    def test_shell(self, call, is_affirmative):
        """The shell clause should make the command run with shell """
        is_affirmative.return_value = True
        self.environment.run_feature("with-shell", 'sync')
        call.assert_called_once_with("echo 'installing...'", shell=True)
