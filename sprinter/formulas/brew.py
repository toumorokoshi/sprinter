"""
Sandboxes a brew installation
[brew]
formula = sprinter.formulas.brew
"""

from sprinter.formulastandard import FormulaStandard
from sprinter import lib


class BrewFormula(FormulaStandard):

    def setup(self, feature_name, config):
        super(CommandFormula, self).setup(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        super(CommandFormula, self).update(feature_name, source_config, target_config)

    def destroy(self, feature_name, config):
        super(CommandFormula, self).destroy(feature_name, config)

    def activate(self, feature_name, config):
        super(CommandFormula, self).activate(feature_name, config)

    def deactivate(self, feature_name, config):
        super(CommandFormula, self).deactivate(feature_name, config)

    def reload(self, feature_name, config):
        super(CommandFormula, self).reload(feature_name, config)
