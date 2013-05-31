from sprinter.testtools import TestFormula
from sprinter.formulas import CommandFormula

formula_config = """
[setup]
formula = sprinter.formulas.command
setup = echo 'setting up...'

[update]
formula = sprinter.formulas.command
update = echo 'update up...'

[destroy]
formula = sprinter.formulas.command
destroy = echo 'destroy up...'
"""


class TestCommandFormula(TestFormula):
    """
    Tests for the command formula.
    """
    def __init__(self):
        super(TestCommandFormula, self).__init__(formula_config)
        self.instance = CommandFormula(self.environment)

    def test_setup(self):
        self.install("setup")
