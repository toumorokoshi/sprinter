"""
Runs a command
[ssh]
formula = sprinter.formula.command
hideoutput=true
install=echo 'setting up...'
update=echo 'updating...'
remove=echo 'destroying...'
activate=echo 'activating...'
deactivate=echo 'deactivating...'
"""
from __future__ import unicode_literals
from sprinter.formulabase import FormulaBase
import sprinter.lib as lib


class CommandFormula(FormulaBase):

    valid_options = FormulaBase.valid_options + ['install', 'update', 'remove', 'activate', 'deactivate']

    def install(self):
        self.__run_command('install', 'target')
        FormulaBase.install(self)

    def update(self):
        self.__run_command('update', 'target')
        FormulaBase.update(self)

    def remove(self):
        self.__run_command('remove', 'source')
        FormulaBase.remove(self)

    def activate(self):
        self.__run_command('activate', 'source')
        FormulaBase.activate(self)

    def deactivate(self):
        self.__run_command('deactivate', 'source')
        FormulaBase.deactivate(self)

    def __run_command(self, command_type, manifest_type):
        config = getattr(self, manifest_type)
        if config.has(command_type):
            command = config.get(command_type)
            self.logger.debug("Running %s..." % command)
            shell = config.has('shell') and config.is_affirmative('shell')
            lib.call(command, shell=shell)
