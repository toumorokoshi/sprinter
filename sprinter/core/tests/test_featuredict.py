from __future__ import unicode_literals
from nose.tools import ok_, eq_
from mock import Mock
from io import StringIO
from six.moves import configparser
from sprinter.core.featuredict import FeatureDict
from sprinter.core.manifest import Manifest

source_config = """
[install_with_rc]
formula = sprinter.formula.base
rc = teststring
""".strip()

target_config = """
[install_with_rc]
formula = sprinter.formula.base
rc = teststring

[install_with_command]
formula = sprinter.formula.base
command = echo 'helloworld'

[osx]
formula = sprinter.formula.base

[osx2]
formula = sprinter.formula.base

[debian]
formula = sprinter.formula.base
""".strip()


class TestFeatureDict():
    """ Tests for the featuredict """

    def setUp(self):
        source_rawconfig = configparser.RawConfigParser()
        source_rawconfig.readfp(StringIO(source_config))
        self.source_manifest = Manifest(source_rawconfig)
                                   
        target_rawconfig = configparser.RawConfigParser()
        target_rawconfig.readfp(StringIO(target_config))
        self.target_manifest = Manifest(target_rawconfig)

        self.feature_dict = FeatureDict(Mock(),
                                        self.source_manifest,
                                        self.target_manifest,
                                        "dummy_path")

    def test_run_order(self):
        """ run_order should return the order in which features should run """
        eq_(self.feature_dict.run_order, [(u'install_with_rc', 'sprinter.formula.base'),
                                          (u'install_with_command', 'sprinter.formula.base'),
                                          (u'osx', 'sprinter.formula.base'),
                                          (u'osx2', 'sprinter.formula.base'),
                                          (u'debian', 'sprinter.formula.base')])
