"""
Specifies environment variables.

[env]
formula = sprinter.formulas.env
stash = %(config:stash)
user = %(config:user)
MAVEN_HOME = %(maven:root_dir)
M2_PATH = ~/.m2/
"""
from sprinter.formulabase import FormulaBase


class EnvFormula(FormulaBase):
    """ A sprinter formula for git"""

    def install(self, feature_name, config):
        [self.directory.add_to_rc('export %s=%s' % (c.upper(), config[c]))
         for c in config if c != 'formula']
        super(EnvFormula, self).install(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        [self.directory.add_to_rc('export %s=%s' % (c.upper(), target_config[c]))
         for c in target_config if c != 'formula']
        super(EnvFormula, self).update(feature_name, source_config, target_config)
