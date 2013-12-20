from __future__ import unicode_literals
from mock import Mock, patch
from sprinter.testtools import FormulaTest
import sprinter.lib as lib

TEST_TARGZ = "http://github.com/toumorokoshi/sprinter/tarball/master"
TEST_ZIP = "http://iterm2.com/downloads/stable/iTerm2_v1_0_0.zip"
TEST_DMG = "https://dl.google.com/chrome/mac/stable/GGRM/googlechrome.dmg"

source_config = """
"""

target_config = """
[targz_with_target]
formula = sprinter.formula.unpack
url = %(targz)s
type = tar.gz
target = /testpath

[dmg_with_target]
formula = sprinter.formula.unpack
url = %(dmg)s
type = dmg
target = /testpath

[zip_with_target]
formula = sprinter.formula.unpack
url = %(zip)s
type = zip
target = /testpath
""" % {'targz': TEST_TARGZ, 'dmg': TEST_DMG, 'zip': TEST_ZIP}


class TestUnpackFormula(FormulaTest):
    """ Tests for the unpack formula """

    def setup(self):
        super(TestUnpackFormula, self).setup(source_config=source_config,
                                             target_config=target_config)

    @patch.object(lib, 'extract_zip')
    def test_zip_with_target(self, extract_zip):
        """ Test the zip extracting to a specific target """
        self.environment.run_feature("zip_with_target", 'sync')
        extract_zip.assert_called_with(TEST_ZIP, '/testpath', remove_common_prefix=False)

    @patch.object(lib, 'extract_dmg')
    def test_dmg_with_target(self, extract_dmg):
        """ Test the dmg extracting to a specific target """
        self.environment.system.isOSX = Mock(return_value=True)
        self.environment.run_feature("dmg_with_target", 'sync')
        extract_dmg.assert_called_with(TEST_DMG, '/testpath', remove_common_prefix=False)

    @patch.object(lib, 'extract_targz')
    def test_targz_with_target(self, extract_targz):
        """ Test the targz extracting to a specific target """
        self.environment.run_feature("targz_with_target", 'sync')
        extract_targz.assert_called_with(TEST_TARGZ, '/testpath', remove_common_prefix=False)
