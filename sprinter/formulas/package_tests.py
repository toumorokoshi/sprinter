from sprinter import testtools
from sprinter.formulas.package import PackageFormula

package_configs = """
[git]
formula = sprinter.formulas.package
apt-get = git
brew = git
"""


class TestPackageFormula(testtools.TestFormula):

    def setUp(self):
        super(TestPackageFormula, self).__init__(formula_config=package_configs)
        self.instance = PackageFormula(self.environment)

    def tearDown(self):
        pass

    def test_command_only_on_package_manager_existence(self):
        """ command should run only if package manager exists """
