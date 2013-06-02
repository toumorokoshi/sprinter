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
        self.__run_command('setup', config)

    def update(self, feature_name, source_config, target_config):
        self.__run_command('update', target_config)

    def remove(self, feature_name, config):
        self.__run_command('remove', config)

    def activate(self, feature_name, config):
        self.__run_command('activate', config)

    def deactivate(self, feature_name, config):
        self.__run_command('deactivate', config)

    def __run_command(self, command_type, config):
        if command_type in config:
            command = config[command_type] % self.environment.context()
            if not 'hideoutput' in config or config['hideoutput'].startswith('t'):
                self.logger.info("Running %s..." % command)
            self.lib.call(command)
