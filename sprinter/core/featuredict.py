from sprinter import lib
from sprinter.lib import SprinterException
from sprinter.external.pippuppet import Pip, PipException
import logging

logger = logging.getLogger(__name__)


class FeatureDict(dict):
    """
    Dictionary which contains instances of features, formulas with a specific configuration
    """

    def __init__(self, environment, source_manifest, target_manifest, pip_install_path, formula_dict=None):
        """ generate a feature dict from Manifests <source_manifest> and <target_manifest> """
        self._environment = environment
        self._run_order = []  # the order with which these features should run
        self._formula_dict = formula_dict or {}  # a dictionary to hold formula classes
        self._pip = Pip(pip_install_path)

        if target_manifest:
            for feature in target_manifest.sections():
                feature_key = self._instantiate_feature(feature, target_manifest, 'target')
                if feature_key:
                    self._run_order.append(feature_key)

        if source_manifest:
            for feature in source_manifest.sections():
                feature_key = self._instantiate_feature(feature, source_manifest, 'source')
                if feature_key:
                    self._run_order.append(feature_key)

    @property
    def run_order(self):
        return self._run_order

    def _instantiate_feature(self, feature, manifest, kind):
        if feature == "config":
            return None
        feature_config = manifest.get_feature_config(feature)
        if feature_config.has('formula'):
            key = (feature, feature_config.get('formula'))
            if key not in self:
                try:
                    formula_class = self._get_formula_class(feature_config.get('formula'))
                    self[key] = formula_class(self._environment, feature, **{kind: feature_config})
                    if self[key].should_run():
                        return key
                    else:
                        del(self[key])
                except SprinterException:
                    self._environment.log_error("ERROR: Invalid formula {0} for {1} feature {2}!".format(
                        feature_config.get('formula'), kind, feature))
            else:
                setattr(self[key], kind, feature_config)
        else:
            self._environment.log_error('feature {0} has no formula!'.format(feature))
        return None

    def _get_formula_class(self, formula):
        """
        get a formula class object if it exists, else
        create one, add it to the dict, and pass return it.
        """
        # recursive import otherwise
        from sprinter.formula.base import FormulaBase
        formula_class, formula_url = formula, None
        if ':' in formula:
            formula_class, formula_url = formula.split(":", 1)
        if formula_class not in self._formula_dict:
            try:
                self._formula_dict[formula_class] = lib.get_subclass_from_module(formula_class, FormulaBase)
            except (SprinterException, ImportError):
                logger.info("Downloading %s..." % formula_class)
                try:
                    self._pip.install_egg(formula_url or formula_class)
                    try:
                        self._formula_dict[formula_class] = lib.get_subclass_from_module(formula_class, FormulaBase)
                    except ImportError:
                        raise SprinterException("Error: Unable to retrieve formula %s!" % formula_class)
                except PipException:
                    logger.error("ERROR: Unable to download %s!" % formula_class)
        return self._formula_dict[formula_class]
