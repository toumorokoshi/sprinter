from mock import Mock
from sprinter.testtools import FormulaTest

source_config = """
"""

target_config = """
"""


class TestUnpackFormula(FormulaTest):
    """ Tests for the unpack formula """

    def setup(self):
        super(TestUnpackFormula, self).setup(source_config=source_config,
                                             target_config=target_config)

    def test_targz_install(self):
        """ """
