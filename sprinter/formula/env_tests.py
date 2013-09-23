from __future__ import unicode_literals
from mock import Mock
from sprinter.testtools import FormulaTest

source_config = """
[simple_update]
formula = sprinter.formula.env
this = doesn't
matter = at all
"""

target_config = """
[simple_example]
formula = sprinter.formula.env
user = toumorokoshi
MAVEN_HOME = ~/bin/mvn
M2_PATH = ~/.m2/

[simple_update]
formula = sprinter.formula.env
a = b
c = dd
e = fgh
"""


class TestEnvFormula(FormulaTest):
    """ Tests for the env formula """

    def setup(self):
        super(TestEnvFormula, self).setup(source_config=source_config,
                                          target_config=target_config)

    def test_simple_example(self):
        """ The env formula should set environment variables """
        self.environment.directory.add_to_env = Mock()
        self.environment.run_feature("simple_example", "sync")
        self.environment.directory.add_to_env.assert_any_call("export USER=toumorokoshi")
        self.environment.directory.add_to_env.assert_any_call("export MAVEN_HOME=~/bin/mvn")
        self.environment.directory.add_to_env.assert_any_call("export M2_PATH=~/.m2/")

    def test_simple_update(self):
        """ The env formula should set environment variables on update """
        self.environment.directory.add_to_env = Mock()
        self.environment.run_feature("simple_update", "sync")
        self.environment.directory.add_to_env.assert_any_call("export A=b")
        self.environment.directory.add_to_env.assert_any_call("export C=dd")
        self.environment.directory.add_to_env.assert_any_call("export E=fgh")
