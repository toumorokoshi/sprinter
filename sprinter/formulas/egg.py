"""
The egg formula will install scripts from an egg (including dependencies) into a sandboxed directory.
[eggs]
formula = sprinter.formulas.egg
egg = sprinter
"""

from sprinter.formulabase import FormulaBase


class EggFormula(FormulaBase):

    def install(self, feature_name, config):
        self.lib.call("easy_install %s" % config['egg'])
        super(EggFormula, self).install(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        self.lib.call("easy_install %s" % target_config['egg'])
        super(EggFormula, self).update(feature_name, source_config, target_config)
