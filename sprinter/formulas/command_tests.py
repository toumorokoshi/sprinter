from sprinter.testtools import TestFormula
from sprinter.formulas import CommandFormula

source_config = """
[update]
formula = sprinter.formulas.command
update = echo 'this is old...'

[destroy]
formula = sprinter.formulas.command
destroy = echo 'destroy up...'

[deactivate]
formula = sprinter.formulas.command
deactivate = echo 'deactivating...'

[activate]
formula = sprinter.formulas.command
deactivate = echo 'activating...'
"""

target_config = """
[setup]
formula = sprinter.formulas.command
setup = echo 'setting up...'
update = echo 'updating...'

[update]
formula = sprinter.formulas.command
update = echo 'update up...'
"""


class TestCommandFormula(TestFormula):
    """
    Tests for the command formula.
    """
    def __init__(self):
        super(TestCommandFormula, self) ._init__(
            CommandFormula,
            target_config=target_config
        )

    def test_setup(self):
        self.install("setup")
        self.lib.call.assert_called_once_with("echo 'setting up...'")

    def test_update(self):
        self.update("update")
        self.lib.call.assert_called_once_with("echo 'update up...'")

    def test_destroy(self):
        self.destroy("destroy")
        self.lib.call.assert_called_once_with("echo 'destroy up...'")

    def test_deactivate(self):
        self.deactivate("deactivate")
        self.lib.call.assert_called_once_with("echo 'deactivate up...'")

    def test_activate(self):
        self.activate("activate")
        self.lib.call.assert_called_once_with("echo 'activate up...'")
