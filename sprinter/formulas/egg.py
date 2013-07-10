"""
The egg formula will install scripts from an egg (including dependencies) into a sandboxed directory.
[eggs]
formula = sprinter.formulas.egg
egg = sprinter
eggs = pelican, pelican-gist
       jedi, epc
"""
import logging
import re
from sprinter.formulabase import FormulaBase
from sprinter.exceptions import CommandMissingException


class EggFormula(FormulaBase):

    def install(self, feature_name, config):
        self.__install_eggs(config)
        super(EggFormula, self).install(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        self.__install_eggs(target_config)
        super(EggFormula, self).update(feature_name, source_config, target_config)

    def __install_eggs(self, config):
        """ Install eggs for a particular configuration """
        eggs = []
        if 'egg' in config:
            eggs += [config['egg']]
        if 'eggs' in config:
            eggs += [egg.strip() for egg in re.split(',|\n', config['eggs'])]
        for egg in eggs:
            self.logger.debug("Installing egg %s..." % egg)
            try:
                self.lib.call("pip install %s" % egg, output_log_level=logging.DEBUG)
            except CommandMissingException:
                self.logger.warn("Unable to install egg %s, please install pip!" % egg)
