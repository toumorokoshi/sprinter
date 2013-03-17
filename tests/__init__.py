import doctest

import sprinter.manifest
import sprinter.lib
from StringIO import StringIO
from sprinter.manifest import Manifest, test_new_version, test_old_version


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(module=sprinter.manifest,
                                        extraglobs={
        'm': Manifest(target_manifest=StringIO(test_new_version), source_manifest=StringIO(test_old_version)),
        'm_new_only': Manifest(target_manifest=StringIO(test_new_version)),
        'm_old_only': Manifest(source_manifest=StringIO(test_old_version))}))
    tests.addTests(doctest.DocTestSuite(module=sprinter.lib))
    return tests
