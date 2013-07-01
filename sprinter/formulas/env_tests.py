from mock import Mock
from sprinter.testtools import FormulaTest

source_config = """
"""

target_config = """
[simple_example]
formula = sprinter.formulas.env
user = toumorokoshi
MAVEN_HOME = ~/bin/mvn
M2_PATH = ~/.m2/
"""


class TestEnvFormula(FormulaTest):
    """ Tests for the env formula """

    def setup(self):
        super(TestEnvFormula, self).setup(source_config=source_config,
                                          target_config=target_config)

    def test_simple_example(self):
        """ The egg formula should install a single egg """
        self.environment.directory.add_to_rc = Mock()
        self.environment.install_feature("simple_example")
        self.environment.directory.add_to_rc.assert_any_call("export USER=toumorokoshi")
        self.environment.directory.add_to_rc.assert_any_call("export MAVEN_HOME=~/bin/mvn")
        self.environment.directory.add_to_rc.assert_any_call("export M2_PATH=~/.m2/")
