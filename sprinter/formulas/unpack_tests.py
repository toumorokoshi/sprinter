from mock import Mock
from sprinter.testtools import FormulaTest

TEST_TARGZ = "http://github.com/toumorokoshi/sprinter/tarball/master"

source_config = """
"""

target_config = """
[targz_with_destination]
formula = sprinter.formulas.unpack
url = %(targz)s
type = tar.gz
destination = '/testpath'
""" % {'targz': TEST_TARGZ}


class TestUnpackFormula(FormulaTest):
    """ Tests for the unpack formula """

    def setup(self):
        super(TestUnpackFormula, self).setup(source_config=source_config,
                                             target_config=target_config)

    def test_targz_with_destination(self):
        """ Test the targz extracting to a specific destination """
        self.environment.install_feature("targz_with_destination")
        self.lib.extract_targz.assert_has_call(TEST_TARGZ, '/testpath', remove_common_prefix=False)
