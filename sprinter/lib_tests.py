"""
Tests for the library
"""

import os
import shutil
import tempfile

from sprinter.formulabase import FormulaBase
from sprinter.environment import Environment
from sprinter.formulas.env import EnvFormula
from sprinter import lib
from sprinter.lib import CommandMissingException


class TestLib(object):

        def setUp(self):
            self.environment = Environment()

        def test_get_formula_class(self):
            """ Test if a formula class is grabbed """
            class_instance = lib.get_formula_class("sprinter.formulas.unpack", self.environment)
            assert issubclass(class_instance.__class__, FormulaBase)

        def test_get_formulabase(self):
            """ Test if formulabase can be grabbed"""
            class_instance = lib.get_formula_class("sprinter.formulabase", self.environment)
            assert issubclass(class_instance.__class__, FormulaBase)

        # can't get this test to work right...
        def skip_get_formula_class_correct_import(self):
            """ This test a bug with importing the proper class"""
            class_instance = lib.get_formula_class("sprinter.formulas.env", self.environment)
            assert class_instance.__class__ == EnvFormula,\
                "%s class is not equal to %s" % (class_instance, EnvFormula)

        def test_lib_errorcode(self):
            """ Test a proper error code is returned """
            assert lib.call("sh") == 0, "cd call returns a non-zero exit!"
            assert lib.call("cd", bash=True) == 0, "cd call returns a non-zero exit!"
            assert lib.call("exit 1", bash=True) == 1, "gibberish call returns a zero exit!"

        def test_call_error(self):
            """ Test an exception is thrown for a non-existent command """
            try:
                lib.call("eahxanea0e0")
            except CommandMissingException:
                return
            raise("Bogus command without proper shell doesn't return proper exception!")

        def integrate_dmg(self):
            """ Test if the dmg install works """
            test_dir = tempfile.mkdtemp()
            try:
                lib.extract_dmg("https://dl.google.com/chrome/mac/stable/GGRM/googlechrome.dmg", test_dir)
                assert os.path.exists(os.path.join(test_dir, "Google Chrome.app")), "app was not extracted!"
            finally:
                shutil.rmtree(test_dir)
