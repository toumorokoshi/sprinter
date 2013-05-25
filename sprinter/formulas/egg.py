"""
The egg formula will install scripts from an egg (including dependencies) into a sandboxed directory.
[eggs]
formula = sprinter.formulas.egg
egg = sprinter
"""

from setuptools.command.easy_install import main as easy_install
from sprinter.formulastandard import FormulaStandard


class EggFormula(FormulaStandard):

    def __init__(self, environment):
        super(EggFormula, self).__init__(environment)

    def setup(self, feature_name, config):
        call("easy_install %s" % config['egg'])
        self.__install_package(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        super(EggFormula, self).update(feature_name, source_config, target_config)
