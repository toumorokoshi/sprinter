import os
import shutil
import tempfile
import unittest
from StringIO import StringIO

from sprinter.manifest import Manifest

manifest_old = """
[config]
namespace = sprinter

[maven]
recipe = sprinter.recipes.unpack
specific_version = 2.10

[ant]
recipe = sprinter.recipes.unpack
specific_version = 1.8.4

[sub]
recipe = sprinter.recipes.git
depends = git
url = git://github.com/Toumorokoshi/sub.git
branch = yusuke
rc = temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp

[mysql]
recipe = sprinter.recipes.package
apt-get = libmysqlclient
          libmysqlclient-dev
brew = mysql

[git]
recipe = sprinter.recipes.package
apt-get = git-core
brew = git
"""

manifest_incorrect_dependency = """
[config]
namespace = sprinter

[sub]
recipe = sprinter.recipes.git
depends = sub
"""

class TestManifest(unittest.TestCase):
    """
    Tests the manifest and config portions of sprinter
    """

    def setUp(self):
        self.manifest_old = Manifest(StringIO(manifest_old))
        self.manifest_incorrect_dependency = Manifest(StringIO(manifest_incorrect_dependency))

    def tearDown(self):
        pass

    def test_dependency_order(self):
        """ Test whether a proper dependency tree generated the correct output. """
        sections = self.manifest_old.recipe_sections()
        self.assertTrue(sections.index('git') < sections.index('sub'), "Dependency is out of order! git comes after sub")

    def test_incorrect_dependency(self):
        """ Test whether an incorrect dependency tree returns an error. """
        self.assertTrue(len(self.manifest_incorrect_dependency.invalidations) > 0, "No errors were produced with an incorrect manifest")


