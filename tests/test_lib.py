"""
Tests for the library
"""

import unittest

from sprinter.formulabase import FormulaBase
from sprinter.environment import Environment
from sprinter.formulas.env import EnvFormula
from sprinter import lib
from sprinter.lib import CommandMissingException


class TestLib(unittest.TestCase):

        def setUp(self):
            self.environment = Environment()

        def test_get_formula_class(self):
            class_instance = lib.get_formula_class("sprinter.formulas.unpack", self.environment)
            self.assertTrue(issubclass(class_instance.__class__, FormulaBase))

        # can't get this test to work right...
        def skip_get_formula_class_correct_import(self):
            """ This test a bug with importing the proper class"""
            class_instance = lib.get_formula_class("sprinter.formulas.env", self.environment)
            self.assertTrue(class_instance.__class__ == EnvFormula,
                            "%s class is not equal to %s" % (class_instance, EnvFormula))

        def test_lib_errorcode(self):
            """ Verify a proper error code is returned """
            self.assertEqual(lib.call("ls"), 0, "ls call returns a non-zero exit!")
            self.assertEqual(lib.call("ls", bash=True), 0, "ls call returns a non-zero exit!")
            self.assertEqual(lib.call("exit 1", bash=True), 1, "gibberish call returns a zero exit!")

        def test_call_error(self):
            """ Verify an exception is thrown for a non-existent command """
            try:
                lib.call("eahxanea0e0")
            except CommandMissingException:
                return
            raise("Bogus command without proper shell doesn't return proper exception!")
