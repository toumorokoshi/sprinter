"""
Tests for the library
"""

import os
import shutil
import tempfile
import unittest

from sprinter.recipebase import RecipeBase
from sprinter.environment import Environment
from sprinter import lib

class TestLib(unittest.TestCase):

	def setUp(self):
		self.environment = Environment()

	def test_get_recipe_class(self):
		class_instance = lib.get_recipe_class("sprinter.recipes.unpack", self.environment)
		self.assertTrue(issubclass(class_instance.__class__, RecipeBase))
