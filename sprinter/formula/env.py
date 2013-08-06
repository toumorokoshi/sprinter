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

    # the keys that should be ignored during write loop (anything that has meaning elsewhere)
    ignored_keys = FormulaBase.valid_options + FormulaBase.required_options

    def install(self):
        for c in (c for c in self.target.keys() if c not in self.ignored_keys):
            self.directory.add_to_env('export %s=%s' % (c.upper(), self.target.get(c)))
        FormulaBase.install(self)

    def update(self):
        for c in (c for c in self.target.keys() if c not in self.ignored_keys):
            self.directory.add_to_env('export %s=%s' % (c.upper(), self.target.get(c)))
        FormulaBase.update(self)

    def validate(self):
        # all config values are valid
        pass
