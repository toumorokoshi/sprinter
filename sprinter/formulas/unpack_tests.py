from mock import Mock
from sprinter.testtools import FormulaTest

TEST_TARGZ = "http://github.com/toumorokoshi/sprinter/tarball/master"
TEST_ZIP = "http://iterm2.com/downloads/stable/iTerm2_v1_0_0.zip"
TEST_DMG = "https://dl.google.com/chrome/mac/stable/GGRM/googlechrome.dmg"

source_config = """
"""

target_config = """
[targz_with_destination]
formula = sprinter.formulas.unpack
url = %(targz)s
type = tar.gz
destination = /testpath

[dmg_with_destination]
formula = sprinter.formulas.unpack
url = %(dmg)s
type = dmg
destination = /testpath

[zip_with_destination]
formula = sprinter.formulas.unpack
url = %(zip)s
type = zip
destination = /testpath
""" % {'targz': TEST_TARGZ, 'dmg': TEST_DMG, 'zip': TEST_ZIP}


class TestUnpackFormula(FormulaTest):
    """ Tests for the unpack formula """

    def setup(self):
        super(TestUnpackFormula, self).setup(source_config=source_config,
                                             target_config=target_config)

    def test_zip_with_destination(self):
        """ Test the zip extracting to a specific destination """
        self.environment.install_feature("zip_with_destination")
        self.lib.extract_zip.assert_has_call(TEST_ZIP, '/testpath', remove_common_prefix=False)

    def test_dmg_with_destination(self):
        """ Test the dmg extracting to a specific destination """
        self.environment.install_feature("dmg_with_destination")
        self.lib.extract_targz.assert_has_call(TEST_DMG, '/testpath', remove_common_prefix=False)

    def test_targz_with_destination(self):
        """ Test the targz extracting to a specific destination """
        self.environment.install_feature("targz_with_destination")
        self.lib.extract_targz.assert_has_call(TEST_TARGZ, '/testpath', remove_common_prefix=False)
