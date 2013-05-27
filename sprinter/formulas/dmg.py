"""
Downloads and mounts a dmg, and copies over desired files.

[intellij]
formula = sprinter.formulas.dmg
url = http://download.jetbrains.com/idea/ideaIC-12.1.3.dmg
"""
import os
import shutil
import tempfile
import urllib
from sprinter.lib import call

from sprinter.formulastandard import FormulaStandard
from sprinter.lib import extract_dmg


class DmgFormula(FormulaStandard):
    """ A sprinter formula for git"""

    def setup(self, feature_name, config):
        extract_dmg(config['url'], self.directory.install_directory(feature_name))
        super(DmgFormula, self).setup(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        if (source_config['formula'] != target_config['formula']
            or source_config['url'] != target_config['url']):
            shutil.rmtree(self.directory.install_directory(feature_name))
            extract_dmg(config['url'], self.directory.install_directory(feature_name))
        super(DmgFormula, self).update(feature_name, source_config, target_config)

    def valid(self, config):
        if 'url' not in config:
            return False
        return True
