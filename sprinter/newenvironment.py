import logging
import os
import sys

from sprinter import virtualenv
from sprinter import brew
from sprinter.directory import Directory
from sprinter.exceptions import SprinterException
from sprinter.injections import Injections
from sprinter.manifest import Config, Manifest
from sprinter.system import System


def warmup(f):
    """ Decorator to run warmup before running a command """

    def wrapped(self, *args, **kwargs):
        if not self.warmed_up:
            self._warmup()
        return f(self, *args, **kwargs)
    return wrapped


def populate_formula_instance(config):
    """ Populate the formula_instance variable if it is none, from the formula config specified """

    def wrapper(f):

        def wrapped(self, formula_name, formula_instance=None):
            if not formula_instance:
                formula_instance = self.__get_formula_instance(
                    self.target,
                    getattr(self, config).get_formula_class(formula_name)
                )
            return f(self, formula_name, formula_instance=formula_instance)
        return wrapped
    return wrapper


class Environment(object):

    source = None  # the path to the source handle, the handle itself, or a manifest instance
    target = None  # the path to the target handle, the handle itself, or a manifest instance
    namespace = None  # the namespace of the environment
    sandboxes = []  # a list of package managers to sandbox (brew, virtualenv)
    # the libraries that environment utilizes
    system = None  # stores utility methods to determine system specifics
    # variables typically populated programatically
    warmed_up = False  # returns true if the environment is ready for environments
    _formula_dict = {}  # a dictionary of existing formula instances to pull from

    def __init__(self, logger=None, logging_level=logging.INFO):
        self.system = System()
        if not logger:
            self.logger = self._build_logger(logging_level=logging.INFO)
        logger.setLevel(logging_level)
        if logging_level == logging.DEBUG:
            self.logger.info("Starting in debug mode...")

    @warmup
    def install(self):
        """ Install the environment """
        self.directory.initialize()

    @warmup
    def update(self):
        """ update the environment """
        if self.directory.new:
            raise SprinterException("Namespace %s is not yet installed!" % self.namespace)

    @warmup
    def remove(self):
        """ remove the environment """
        if self.directory.new:
            raise SprinterException("Namespace %s is not yet installed!" % self.namespace)

    @warmup
    def deactivate(self):
        """ deactivate the environment """

    @warmup
    def activate(self):
        """ activate the environment """

    @warmup
    @populate_formula_instance('target')
    def install_formula(self, formula_name, formula_instance=None):
        """ Install a specific formula """

    @warmup
    @populate_formula_instance('target')
    def update_formula(self, formula_name, formula_instance=None):
        """ Update a specific formula """

    @warmup
    @populate_formula_instance('source')
    def remove_formula(self, formula_name, formula_instance=None):
        """ Remove a specific formula """

    @warmup
    @populate_formula_instance('source')
    def deactivate_formula(self, formula_name, formula_instance=None):
        """ Deactivate a specific formula """

    @warmup
    @populate_formula_instance('source')
    def activate_formula(self, formula_name, formula_instance=None):
        """ Activate a specific formula """

    @warmup
    @populate_formula_instance('target')
    def validate_formula(self, formula_name, formula_instance=None):
        """ Validate a specific formula """

    @warmup
    def validate_manifest(self, manifest):
        """ Validate a manifest object """
        invalidations = manifest.invalidations
        for s in self.target.formula_sections():
            invalidations += self.validate_formula(self, s)
        return invalidations
        
    def _warmup(self):
        """ initialize variables necessary to perform a sprinter action """
        self.log.debug("Warming up...")
        if not isinstance(self.source, Manifest) and self.source:
            self.source = Manifest(self.source)
        if not isinstance(self.target, Manifest) and self.target:
            self.target = Manifest(self.target)
        self.config = Config(source=self.source, target=self.target,
                             namespace=self.namespace)
        if not self.namespace:
            self.namespace = self.config.namespace
        if not self.directory:
            self.directory = Directory(self.namespace)
        self.injections = Injections(wrapper="SPRINTER_%s" % self.namespace)
        # install virtualenv
        self._install_sandbox('virtualenv', virtualenv.create_environment,
                              {'use_distribute': True})
        if self.system.isOSX():
            self._install_sandbox('brew', brew.install_brew)
        # append the bin, in the case sandboxes are necessary to
        # execute commands further down the sprinter lifecycle
        os.environ['PATH'] = self.directory.bin_path() + ":" + os.environ['PATH']

    def _install_sandbox(self, name, call, kwargs={}):
        if (self.target.is_true('config', name) and
           (not self.source or not self.source.is_true('config', name))):
            self.logger.info("Installing %s..." % name)
            call(self.directory.root_dir, **kwargs)

    def _build_logger(self, logger=None, level=logging.INFO):
        """ return a logger. if logger is none, generate a logger from stdout """
        logger = logging.getLogger('sprinter')
        out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        out_hdlr.setLevel(level)
        logger.addHandler(out_hdlr)
        return logger

    def __get_formula_instance(self, formula):
        """
        get an instance of the formula object object if it exists, else
        create one, add it to the dict, and pass return it.
        """
        if formula not in self._formula_dict:
            self._formula_dict[formula] = get_formula_class(formula, self)
        return self._formula_dict[formula]

