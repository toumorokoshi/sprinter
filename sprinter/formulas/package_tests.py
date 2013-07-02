from sprinter.formulas.package import PackageFormula
from mock import Mock, call
from sprinter.testtools import FormulaTest
from nose.plugins.attrib import attr

source_config = """
[no_update]
formula = sprinter.formulas.package
apt-get = gitA

[update_new_formula]
formula = sprinter.formulas.formulabase
apt-get = gitA

[update_new_package]
formula = sprinter.formulas.package
apt-get = gitA
"""

target_config = """
[simple_example]
formula = sprinter.formulas.package
brew = git
apt-get = git-core
yum = git-core

[no_update]
formula = sprinter.formulas.package
apt-get = gitA

[update_new_formula]
formula = sprinter.formulas.package
apt-get = gitA

[update_new_package]
formula = sprinter.formulas.package
apt-get = gitB
"""


class TestPackageFormula(FormulaTest):

    def setup(self):
        super(TestPackageFormula, self).setup(source_config=source_config,
                                              target_config=target_config)
        self.environment.system.isDebianBased = Mock(return_value=True)
        self.environment.system.isOSX = Mock(return_value=False)
        self.environment.system.isFedoraBased = Mock(return_value=False)

    def test_simple_example_osx(self):
        """ A brew package should install on osx """
        self.environment.system.isOSX = Mock(return_value=True)
        self.environment.system.isDebianBased = Mock(return_value=False)
        self.environment.system.isFedoraBased = Mock(return_value=False)
        self.environment.install_feature("simple_example")
        self.lib.call.assert_called_with("brew install git")

    def test_simple_example_debian(self):
        """ An apt-get package should install on debian """
        self.environment.system.isDebianBased = Mock(return_value=True)
        self.environment.system.isOSX = Mock(return_value=False)
        self.environment.system.isFedoraBased = Mock(return_value=False)
        self.environment.install_feature("simple_example")
        self.lib.call.assert_called_with("sudo apt-get -y install git-core")

    def test_simple_example_fedora(self):
        """ A yum package should install properly on fedora """
        self.environment.system.isFedoraBased = Mock(return_value=True)
        self.environment.system.isDebianBased = Mock(return_value=False)
        self.environment.system.isOSX = Mock(return_value=False)
        self.environment.install_feature("simple_example")
        self.lib.call.assert_called_with("sudo yum install git-core")

    def test_no_update(self):
        """ An unchanged formula should not be updated """
        self.environment.update_feature("no_update")
        assert not self.lib.call.called, "Update was called!"

    def test_update_different_formula(self):
        """ An feature with a new formula """
        self.environment.update_feature("update_new_formula")
        self.lib.call.assert_called_with("sudo apt-get install gitA")

    def test_update_different_formula(self):
        """ An feature with a new formula """
        self.environment.update_feature("update_new_package")
        self.lib.call.assert_called_with("sudo apt-get -y install gitB")
