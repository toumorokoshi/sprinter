from ..core import PHASE
from .common import execute_commmon_functionality


class Feature(object):
    """
    A feature is effectively a parameterized Formula. This class
    exists to ensure some common functionality across all formulas.
    """

    def __init__(self, formula_instance):
        # remove once setattr no longer needed to be overriden.
        self.__dict__["_formula_instance"] = formula_instance

    @property
    def instance(self):
        """return the formula instance"""
        return self._formula_instance

    def install(self):
        result = self._formula_instance.install()
        execute_commmon_functionality(self._formula_instance)
        return result

    def update(self):
        result = self._formula_instance.update()
        execute_commmon_functionality(self._formula_instance)
        return result

    def remove(self):
        result = self._formula_instance.remove()
        self._formula_instance.directory.remove_feature(self.feature_name)
        return result

    def sync(self):
        """
        execute the steps required to have the
        feature end with the desired state.
        """
        phase = _get_phase(self._formula_instance)
        self.logger.info("%s %s..." % (phase.verb.capitalize(), self.feature_name))
        message = "...finished %s %s." % (phase.verb, self.feature_name)
        result = getattr(self, phase.name)()
        if result or phase in (PHASE.INSTALL, PHASE.REMOVE):
            self.logger.info(message)
        else:
            self.logger.debug(message)
        return result

    def __getattr__(self, key):
        """fallback behavior to formula instance"""
        return getattr(self._formula_instance, key)

    def __setattr__(self, key, value):
        """
        support legacy behavior of directly setting values against
        the formula instance.

        this is being used to set source/target manifests. A little contrived.
        Looking toward the future, we should work toward all values necessary
        passed in to the constructor, or a separate config object.
        """
        return setattr(self._formula_instance, key, value)


def _get_phase(formula_instance):
    if not formula_instance.source:
        return PHASE.INSTALL
    if not formula_instance.target:
        return PHASE.REMOVE
    return PHASE.UPDATE
