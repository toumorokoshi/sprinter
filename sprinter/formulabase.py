
"""
Formula base is an abstract base class outlining the method required
and some documentation on what they should provide.
"""
import logging
import os

from sprinter.core import LOGGER, PHASE
from sprinter.exceptions import FormulaException


class FormulaBase(object):

    def __init__(self, environment, feature_name, source=None, target=None, logger=LOGGER):
        """
        In most cases, it is not a good idea to override the formulabase
        init method. Sprinter calls it in a very specific fashion, and
        to set it up otherwise risks incompatibility
        """
        self.feature_name = feature_name
        self.source = source
        self.target = target
        if not (source or target):
            raise FormulaException("A formula requires a source and/or a target!")
        self.environment = environment
        self.directory = environment.directory
        self.config = environment.config
        self.injections = environment.injections
        self.system = environment.system
        self.logger = LOGGER

    def prompt(self):
        """
        This call should contain as much of the user input as possible. Examples include:

        * prompting for options regarding configuration
        * overriding existing files/configuration

        prompt's are brought up at the beginning of sprinter's
        instantiation, before any action's are taken.

        prompt, as with all sprinter actions, should return a list of errors
        """
        return []

    def install(self):
        """
        Install is called when a feature does not previously exist. 

        In the case of a feature changing formulas, the old feature/formula is
        removed, then the new feature/formula is installed.
        
        Installs are only guaranteed to have the 'target' config set.

        install, as with all sprinter actions, should return a list of errors
        """
        install_directory = self.directory.install_directory(self.feature_name)
        cwd = install_directory if os.path.exists(install_directory) else None
        if self.target.has('rc'):
            self.directory.add_to_rc(self.target.get('rc'))
        if self.target.has('command'):
            self.lib.call(self.target.get('command'), shell=True, cwd=cwd)
        return []

    def update(self):
        """ 
        Update is called when a feature previously exists, with the same formula

        Updates are guaranteed to have both the 'source' and 'target' configs set

        update, as with all sprinter actions, should return a list of errors
        """
        return self.install()

    def remove(self):
        """
        Remove is called when a feature no longer exists. 

        remove will delete the feature directory before it is
        done. Most of the time, no other action should be necessary.

        remove is guaranteed to have only the 'source' config.

        remove, as with all sprinter actions, should return a list of errors
        """
        return []

    def deactivate(self):
        """ 
        Deactivate is called when a user deactivates the environment. 

        deactivate will deactivate an environment. Deactivate disables the .rc file for a sprinter install, 
        so any extra functionality should be removed here:

        * configuration in a global location, such as an ssh configuration

        deactivate, as with all sprinter actions, should return a list of errors
        """
        return []

    def activate(self):
        """ 
        Activate is called when a user activates the environment. 
        
        activate should inject configuration into the environment. Activate enables the .rc file for a sprinter install,
        so any extra functionality should be added here:

        * configuration in a global location, such as an ssh configuration

        activate, as with all sprinter actions, should return a list of errors
        """
        return []

    def validate(self):
        """
        validates the feature configuration, and returns a list of errors (empty list if no error)
        
        validate should:

        * required variables
        * warn on unused variables

        validate, as with all sprinter actions, should return a list of errors
        """
        return []

    # these methods are overwritten less often, and are not recommended to do so.
    def should_run(self):
        """ Returns true if the feature should run """
        config = self.target or self.source
        if config.has('systems'):
            valid_systems = [s.lower() for s in config.get('systems').split(",")]
            for system_type, param in [('isOSX', 'osx'),
                                       ('isDebianBased', 'debian')]:
                if param in valid_systems and getattr(self.system, system_type)() is True:
                    should_run = True
        return False
            
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
