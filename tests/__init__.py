import doctest

import sprinter.manifest
import sprinter.lib
from StringIO import StringIO
from sprinter.manifest import Manifest, Config, test_new_version, test_old_version


def load_tests(loader, tests, ignore):
    # globs for manifest
    old_manifest = Manifest(StringIO(test_old_version))
    new_manifest = Manifest(StringIO(test_new_version))
    config = Config(source=old_manifest, target=new_manifest)
    tests.addTests(doctest.DocTestSuite(module=sprinter.manifest,
                                        extraglobs={'c': config,
                                                    'new_manifest': new_manifest,
                                                    'old_manifest': old_manifest}))
    tests.addTests(doctest.DocTestSuite(module=sprinter.lib))
    return tests
