"""
Queries the user for a specific environment

[env]
formula = sprinter.formulas.env
stash = %(config:stash)
user = %(config:user)
MAVEN_HOME = %(maven:root_dir)
M2_PATH = ~/.m2/
"""
from sprinter.formulastandard import FormulaStandard


class EnvFormula(FormulaStandard):
    """ A sprinter formula for git"""

    def setup(self, feature_name, config):
        super(EnvFormula, self).setup(feature_name, config)
        [self.directory.add_to_rc('export %s=%s' % (c.upper(), config[c]))
         for c in config if c != 'formula']

    def update(self, feature_name, config):
        super(EnvFormula, self).update(feature_name, config)
        [self.directory.add_to_rc('export %s=%s' % (c.upper(), config['target'][c]))
         for c in config['target'] if c != 'formula']

    def destroy(self, feature_name, config):
        super(EnvFormula, self).destroy(feature_name, config)
        pass
