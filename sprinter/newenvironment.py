import logging
import os
import shutil
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


def install_required(f):
    """ Return an exception if the namespace is not already installed """

    def wrapped(self, *args, **kwargs):
        if self.directory.new:
            raise SprinterException("Namespace %s is not yet installed!" % self.namespace)
        return f(self, *args, **kwargs)
    return wrapped


def populate_formula_instance(config):
    """ Populate the formula_instance variable if it is none, from the formula config specified """

    def wrapper(f):

        def wrapped(self, feature_name, formula_instance=None):
            if not formula_instance:
                formula_instance = self.__get_formula_instance(
                    self.target,
                    getattr(self, config).get_feature_class(feature_name)
                )
            return f(self, feature_name, formula_instance=formula_instance)
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
        if not self.directory.new:
            self.logger.info("Namespace %s already exists!")
            return self.update()
        self.logger.info("Installing environment %s..." % self.namespace)
        self.directory.initialize()
        for feature in self.config.setups():
            self.install_feature(feature)
        self.injections.inject("~/.bash_profile", "[ -d %s ] && . %s/.rc" %
                               (self.directory.root_dir, self.directory.root_dir))
        self.injections.inject("~/.bashrc", "[ -d %s ] && . %s/.rc" %
                               (self.directory.root_dir, self.directory.root_dir))
        self._finalize()
        
    @warmup
    @install_required
    def update(self):
        """ update the environment """
        self.logger.info("Updating environment %s..." % self.namespace)
        for feature in self.config.setups():
            self.install_feature(feature)
        for feature in self.config.updates():
            self.update_feature(feature)
        for feature in self.config.removes():
            self.remove_feature(feature)
        self._finalize()

    @warmup
    @install_required
    def remove(self):
        """ remove the environment """
        self.logger.info("Removing environment %s..." % self.namespace)
        for feature in self.config.removes():
            self.remove_feature(feature)
        self.injections.clear("~/.bash_profile")
        shutil.rmtree(self.directory.root_dir)
        self._finalize()

    @warmup
    @install_required
    def deactivate(self):
        """ deactivate the environment """
        self.directory.rewrite_rc = False
        for feature in self.config.deactivations():
            self.deactivate_feature(feature)
        self.injections.clear("~/.bash_profile")
        self._finalize()

    @warmup
    @install_required
    def activate(self):
        """ activate the environment """
        self.directory.rewrite_rc = False
        for feature in self.config.activations():
            self.activate_feature(feature)
        self.injections.inject("~/.bash_profile", "[ -d %s ] && . %s/.rc" %
                               (self.directory.root_dir, self.directory.root_dir))
        self.injections.inject("~/.bashrc", "[ -d %s ] && . %s/.rc" %
                               (self.directory.root_dir, self.directory.root_dir))
        self._finalize()

    @warmup
    @populate_formula_instance('target')
    def install_feature(self, feature_name, formula_instance=None):
        """ Install a specific formula """
        return self._run_action("Installing", feature_name, formula_instance.install, ['target'])

    @warmup
    @populate_formula_instance('target')
    def update_feature(self, feature_name, formula_instance=None):
        """ Update a specific formula """
        return self._run_action("Updating", feature_name, formula_instance.update, ['source', 'target'])

    @warmup
    @populate_formula_instance('source')
    def remove_feature(self, feature_name, formula_instance=None):
        """ Remove a specific formula """
        return self._run_action("Removing", feature_name, formula_instance.remove, 'source')

    @warmup
    @populate_formula_instance('source')
    def deactivate_feature(self, feature_name, formula_instance=None):
        """ Deactivate a specific formula """
        return self._run_action("Deactivating", feature_name, formula_instance.deactivate, 'source')

    @warmup
    @populate_formula_instance('source')
    def activate_feature(self, feature_name, formula_instance=None):
        """ Activate a specific formula """
        return self._run_action("Activating", feature_name, formula_instance.activate, 'source')

    @warmup
    @populate_formula_instance('target')
    def validate_feature(self, feature_name, formula_instance=None):
        """ Validate a specific formula """
        return self._run_action("Activating", feature_name, formula_instance.activate, 'target')

    @warmup
    def validate_manifest(self, manifest):
        """ Validate a manifest object """
        invalidations = manifest.invalidations
        for s in self.target.formula_sections():
            invalidations += self.validate_feature(self, s)
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

    def _finalize(self):
        """ command to run at the end of sprinter's run """
        self.logger.debug("Finalizing...")
        if os.path.exists(self.directory.manifest_path):
            self.config.write(open(self.directory.manifest_path, "w+"))
        if self.directory.rewrite_rc:
            self.directory.add_to_rc("export PATH=%s:$PATH" % self.directory.bin_path())
        self.injections.commit()

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
            self._formula_dict[formula] = self.manifest.get_formula_class(formula, self)
        return self._formula_dict[formula]

    def __run_action(self, adjective, feature_name, call, configs):
        self.logger.info("%s %s..." % (adjective, feature_name))
        configs = [getattr(self.config, c).get_feature_config(feature_name) for c in configs]
        call(feature_name, *configs)

    def specialize_contexts(self):
        """ Add variables and specialize contexts """
        # add in the 'root_dir' directories to the context dictionaries
        for manifest in [self.source, self.target]:
            context_dict = {}
            for s in manifest.formula_sections():
                context_dict["%s:root_dir" % s] = self.directory.install_directory(s)
            context_dict['config:node'] = self.system.node
            manifest.additional_context_variables = context_dict
