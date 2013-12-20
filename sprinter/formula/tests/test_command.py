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

[failure]
formula = sprinter.formula.command
install = exit 1
fail_on_error = true

[failure_no_error]
formula = sprinter.formula.command
install = exit 1
fail_on_error = false
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
        
    @patch.object(lib, 'call')
    def test_failure(self, call):
        """ If a failure occurs and fail_on_error is true, raise an error """
        call.return_value = (1, "dummy")
        self.environment.run_feature('failure', 'sync')
        assert self.environment.error_occured

    @patch.object(lib, 'call')
    def test_failure_no_fail_on_error(self, call):
        """ If a failure occurs and fail_on_error is false, don't raise an error """
        call.return_value = (1, "dummy")
        self.environment.run_feature('failure_no_error', 'sync')
        assert not self.environment.error_occured

    @patch.object(lib, 'is_affirmative')
    @patch.object(lib, 'call')
    def test_shell(self, call, is_affirmative):
        """The shell clause should make the command run with shell """
        is_affirmative.return_value = True
        self.environment.run_feature("with-shell", 'sync')
        call.assert_called_once_with("echo 'installing...'", shell=True)
