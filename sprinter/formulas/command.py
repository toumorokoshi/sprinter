"""
Runs a command
[ssh]
formula = sprinter.formulas.command
hideoutput=true
setup=echo 'setting up...'
update=echo 'updating...'
remove=echo 'destroying...'
activate=echo 'activating...'
deactivate=echo 'deactivating...'
"""
from sprinter.formulabase import FormulaBase


class CommandFormula(FormulaBase):

    def install(self, feature_name, config):
        self.__run_command('setup', config, 'target')

    def update(self, feature_name, source_config, target_config):
        self.__run_command('update', target_config, 'target')

    def remove(self, feature_name, config):
        self.__run_command('remove', config, 'source')

    def activate(self, feature_name, config):
        self.__run_command('activate', config, 'source')

    def deactivate(self, feature_name, config):
        self.__run_command('deactivate', config, 'source')

    def __run_command(self, command_type, config, manifest_type):
        if command_type in config:
            command = config[command_type] % self.config.context(manifest_type)
            self.logger.info("Running %s..." % command)
            self.lib.call(command)
