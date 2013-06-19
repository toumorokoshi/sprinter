"""
Runs a command
[ssh]
formula = sprinter.formulas.command
hideoutput=true
install=echo 'setting up...'
update=echo 'updating...'
remove=echo 'destroying...'
activate=echo 'activating...'
deactivate=echo 'deactivating...'
"""
from sprinter.formulabase import FormulaBase


class CommandFormula(FormulaBase):

    def install(self, feature_name, config):
        self.__run_command('install', config, 'target')
        super(CommandFormula, self).install(feature_name, config)

    def update(self, feature_name, source_config, target_config):
        self.__run_command('update', target_config, 'target')
        super(CommandFormula, self).update(feature_name, source_config, target_config)

    def remove(self, feature_name, config):
        self.__run_command('remove', config, 'source')
        super(CommandFormula, self).remove(feature_name, config)

    def activate(self, feature_name, config):
        self.__run_command('activate', config, 'source')
        super(CommandFormula, self).activate(feature_name, config)

    def deactivate(self, feature_name, config):
        self.__run_command('deactivate', config, 'source')
        super(CommandFormula, self).deactivate(feature_name, config)

    def __run_command(self, command_type, config, manifest_type):
        if command_type in config:
            command = config[command_type] % self.config.context(manifest_type)
            self.logger.info("Running %s..." % command)
            bash = 'bash' in config and self.lib.is_affirmative(config['bash'])
            self.lib.call(command, bash=bash)
