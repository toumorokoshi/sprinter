from __future__ import unicode_literals
import logging
from mock import Mock, patch
from sprinter.testtools import FormulaTest
import sprinter.lib as lib


source_config = """
[no_update]
formula = sprinter.formula.package
apt-get = gitA

[update_new_package]
formula = sprinter.formula.package
apt-get = gitA
"""

target_config = """
[simple_example]
formula = sprinter.formula.package
brew = git
apt-get = git-core
yum = git-core

[no_update]
formula = sprinter.formula.package
apt-get = gitA

[update_new_package]
formula = sprinter.formula.package
apt-get = gitB
"""


class TestPackageFormula(FormulaTest):

    def setup(self):
        super(TestPackageFormula, self).setup(source_config=source_config,
                                              target_config=target_config)
        self.environment.system.isDebianBased = Mock(return_value=False)
        self.environment.system.isOSX = Mock(return_value=False)
        self.environment.system.isFedoraBased = Mock(return_value=False)
        self.which_original = lib.which
        lib.which = Mock(return_value=True)

    def teardown(self):
        lib.which = self.which_original

    @patch.object(lib, 'call')
    def test_simple_example_osx(self, call):
        """ A brew package should install on osx """
        self.environment.system.isOSX = Mock(return_value=True)
        self.environment.run_feature('simple_example', 'sync')
        call.assert_called_with("brew install git", output_log_level=logging.DEBUG, stdout=None)

    @patch.object(lib, 'call')
    def test_simple_example_debian(self, call):
        """ An apt-get package should install on debian """
        self.environment.system.isDebianBased = Mock(return_value=True)
        self.environment.run_feature('simple_example', 'sync')
        call.assert_called_with("sudo apt-get -y install git-core", output_log_level=logging.DEBUG, stdout=None)

    @patch.object(lib, 'call')
    def test_simple_example_fedora(self, call):
        """ A yum package should install properly on fedora """
        self.environment.system.isFedoraBased = Mock(return_value=True)
        self.environment.run_feature('simple_example', 'sync')
        call.assert_called_with("sudo yum install git-core", output_log_level=logging.DEBUG, stdout=None)

    @patch.object(lib, 'call')
    def test_no_update(self, call):
        """ An unchanged formula should not be updated """
        self.environment.run_feature('no_update', 'sync')
        assert not call.called, "Update was called!"

    @patch.object(lib, 'call')
    def test_update_different_package(self, call):
        """ An feature with a new formula """
        self.environment.system.isDebianBased = Mock(return_value=True)
        self.environment.run_feature('update_new_package', 'sync')
        call.assert_called_with("sudo apt-get -y install gitB", output_log_level=logging.DEBUG, stdout=None)
