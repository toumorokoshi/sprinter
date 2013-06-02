from sprinter import testtools
from sprinter.formulas.package import PackageFormula

package_configs = """
[git]
formula = sprinter.formulas.package
apt-get = git
brew = git
"""


class TestPackageFormula(object):

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_command_only_on_package_manager_existence(self):
        """ command should run only if package manager exists """

    def test_setup(self):
        """ Test the setup method """
