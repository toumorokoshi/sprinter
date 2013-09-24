
"""
Formula base is an abstract base class outlining the method required
and some documentation on what they should provide.
"""
import os

from sprinter.core import LOGGER, PHASE
from sprinter.exceptions import FormulaException
import sprinter.lib as lib


class FormulaBase(object):

    valid_options = ['rc', 'env', 'command', 'systems', 'depends', 'inputs']
    required_options = ['formula']

    def __init__(self, environment, feature_name, source=None, target=None, logger=LOGGER):
        """
        In most cases, it is not a good idea to override the formulabase
        init method. Sprinter calls it in a very specific fashion, and
        to set it up otherwise risks incompatibility
        """
        self.feature_name = feature_name
        self.source = source
        self.target = target
        self.environment = environment
        self.directory = environment.directory
        self.system = environment.system
        self.injections = environment.injections
        if not (source or target):
            raise FormulaException("A formula requires a source and/or a target!")
        self.logger = LOGGER

    def prompt(self):
        """
        This call should contain as much of the user input as possible. Examples include:

        * prompting for options regarding configuration
        * overriding existing files/configuration

        prompt's are brought up at the beginning of sprinter's
        instantiation, before any action's are taken.
        """

    def install(self):
        """
        Install is called when a feature does not previously exist.

        In the case of a feature changing formulas, the old feature/formula is
        removed, then the new feature/formula is installed.
        
        Installs are only guaranteed to have the 'target' config set.

        errors should either be reported via self._log_error(), or raise an exception
        """
        install_directory = self.directory.install_directory(self.feature_name)
        cwd = install_directory if os.path.exists(install_directory) else None
        if self.target.has('env'):
            self.directory.add_to_env(self.target.get('env'))
        if self.target.has('rc'):
            self.directory.add_to_rc(self.target.get('rc'))
        if self.target.has('command'):
            lib.call(self.target.get('command'), shell=True, cwd=cwd)

    def update(self):
        """
        Update is called when a feature previously exists, with the same formula

        Updates are guaranteed to have both the 'source' and 'target' configs set

        errors should either be reported via self._log_error(), or raise an exception
        """
        return FormulaBase.install(self)

    def remove(self):
        """
        Remove is called when a feature no longer exists.

        remove will delete the feature directory before it is
        done. Most of the time, no other action should be necessary.

        remove is guaranteed to have only the 'source' config.

        errors should either be reported via self._log_error(), or raise an exception
        """
        self.directory.remove_feature(self.feature_name)

    def deactivate(self):
        """
        Deactivate is called when a user deactivates the environment.

        deactivate will deactivate an environment. Deactivate disables
        the .rc file for a sprinter install, so any extra functionality
        should be removed here:

        * configuration in a global location, such as an ssh configuration

        errors should either be reported via self._log_error(), or raise an exception
        """

    def activate(self):
        """
        Activate is called when a user activates the environment.
        
        activate should inject configuration into the environment. Activate enables the .rc file for a sprinter install,
        so any extra functionality should be added here:

        * configuration in a global location, such as an ssh configuration
        
        errors should either be reported via self._log_error(), or raise an exception
        """

    def validate(self):
        """
        validates the feature configuration, and returns a list of errors (empty list if no error)
        
        validate should:

        * required variables
        * warn on unused variables

        errors should either be reported via self._log_error(), or raise an exception
        """
        if self.target:
            for k in self.target.keys():
                if k not in self.valid_options and k not in self.required_options:
                    self.logger.warn("Unused option %s in %s!" % (k, self.feature_name))
            for k in self.required_options:
                if not self.target.has(k):
                    self._log_error("Required option %s not present in feature %s!" % (k, self.feature_name))

    # these methods are overwritten less often, and are not recommended to do so.
    def should_run(self):
        """ Returns true if the feature should run """
        should_run = True
        config = self.target or self.source
        if config.has('systems'):
            should_run = False
            valid_systems = [s.lower() for s in config.get('systems').split(",")]
            for system_type, param in [('isOSX', 'osx'),
                                       ('isDebianBased', 'debian')]:
                if param in valid_systems and getattr(self.system, system_type)():
                    should_run = True
        return should_run
            
    def sync_phase(self):
        """ Says whether a sync is an install, update, or delete """
        if not self.source:
            return PHASE.INSTALL
        if not self.target:
            return PHASE.REMOVE
        return PHASE.UPDATE

    def sync(self):
        """ Updates the state of the feature to what it should be """
        phase = self.sync_phase()
        self.logger.info("%s %s..." % (phase.verb, self.feature_name))
        return getattr(self, phase.name)()

    def resolve(self):
        """ Resolve differences between the target and the source configuration """
        if self.source and self.target:
            for k in (k for k in self.source.keys() if not self.target.has(k)):
                self.target.set(k, self.source.get(k))

    def _log_error(self, message):
        """ Log an error for the feature """
        key = (self.feature_name, self.target.get('formula'))
        self.environment.log_feature_error(key, "ERROR: " + message)
