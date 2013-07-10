import logging
from sprinter.testtools import FormulaTest

source_config = """
"""

target_config = """
[simple_example]
formula = sprinter.formulas.egg
egg = jedi

[simple_multiple_eggs]
formula = sprinter.formulas.egg
eggs = jedi, epc=0.5
       pelican

[simple_multiple_and_single_eggs]
formula = sprinter.formulas.egg
egg = sprinter
eggs = jedi, epc=0.5
       pelican

[sprinter]
formula = sprinter.formulas.egg
egg = http://github.com/toumorokoshi/sprinter/tarball/master
"""


class TestEggFormula(FormulaTest):
    """ Tests for the egg formula """

    def setup(self):
        super(TestEggFormula, self).setup(source_config=source_config,
                                          target_config=target_config)

    def test_simple_example(self):
        """ The egg formula should install a single egg """
        self.environment.install_feature("simple_example")
        self.lib.call.assert_called_with("pip install jedi", output_log_level=logging.DEBUG)

    def test_simple_multiple_eggs(self):
        """ The egg formula should install multiple eggs """
        self.environment.install_feature("simple_multiple_eggs")
        self.lib.call.assert_any_call("pip install jedi", output_log_level=logging.DEBUG)
        self.lib.call.assert_any_call("pip install epc=0.5", output_log_level=logging.DEBUG)
        self.lib.call.assert_any_call("pip install pelican", output_log_level=logging.DEBUG)

    def test_simple_multiple_and_single_eggs(self):
        """ The egg formula should install single and multiple eggs """
        self.environment.install_feature("simple_multiple_and_single_eggs")
        self.lib.call.assert_any_call("pip install jedi", output_log_level=logging.DEBUG)
        self.lib.call.assert_any_call("pip install epc=0.5", output_log_level=logging.DEBUG)
        self.lib.call.assert_any_call("pip install pelican", output_log_level=logging.DEBUG)
        self.lib.call.assert_any_call("pip install sprinter", output_log_level=logging.DEBUG)

    def test_sprinter(self):
        """ The sprinter egg formula should install sprinter from a remote protocol """
        self.environment.install_feature("sprinter")
        self.lib.call.assert_called_with("pip install http://github.com/toumorokoshi/sprinter/tarball/master",
                                         output_log_level=logging.DEBUG)

    def test_no_pip(self):
        """ The egg formula should install single and multiple eggs """
        pass
