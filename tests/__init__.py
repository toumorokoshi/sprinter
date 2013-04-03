import doctest

import sprinter.manifest
import sprinter.lib
from StringIO import StringIO
from sprinter.manifest import Manifest, Config, test_new_version, test_old_version

TEST_MANIFEST = \
"""
[config]
inputs = stashroot==~/p4
         username
         password?
         main_branch==comp_main
[sub]
recipe = sprinter.recipes.git
url = git://github.com/Toumorokoshi/sub.git
branch = yusuke
rc = temp=`pwd`; cd %(sub:root_dir)s/libexec && . sub-init2 && cd $tmp
[m2]
recipe = sprinter.recipes.template
target = ~/.m2/settings.bak
source = https://raw.github.com/Toumorokoshi/EmacsEnv/master/.vimrc
[perforce]
inputs = p4passwd?
recipe = sprinter.recipes.perforce
version = r10.1
username = %(config:username)
password = %(config:p4passwd)
client = perforce.local:1666
"""
def load_tests(loader, tests, ignore):
    # globs for manifest
    old_manifest = Manifest(StringIO(test_old_version))
    new_manifest = Manifest(StringIO(test_new_version))
    config = Config(source=old_manifest, target=new_manifest)
    config_new_only = Config(target=new_manifest)
    config_old_only = Config(source=old_manifest)
    tests.addTests(doctest.DocTestSuite(module=sprinter.manifest,
                                        extraglobs={'c': config,
                                                    'config_new_only': config_new_only,
                                                    'config_old_only': config_old_only}))
    tests.addTests(doctest.DocTestSuite(module=sprinter.lib))
    return tests
