import logging
from mock import Mock, patch
from sprinter.testtools import FormulaTest
import sprinter.lib as lib
from sprinter.buildoutpuppet import BuildoutPuppet
from nose.plugins.attrib import attr

source_config = """
"""

target_config = """
[simple_example]
formula = sprinter.formula.eggscript
egg = sprinter

[simple_multiple_eggs]
formula = sprinter.formula.eggscript
eggs = jedi, epc==0.5
       pelican

[simple_multiple_and_single_eggs]
formula = sprinter.formula.eggscript
egg = sprinter
eggs = jedi, epc==0.5
       pelican

[sprinter]
formula = sprinter.formula.eggscript
egg = sprinter
links = http://github.com/toumorokoshi/sprinter/tarball/master#sprinter-0.6
"""


class TestEggscriptFormula(FormulaTest):
    """ Tests for the egg formula """

    def setup(self):
        super(TestEggscriptFormula, self).setup(source_config=source_config,
                                                target_config=target_config)

    @attr('full')
    def skip_simple_example(self):
        """ The egg formula should install a single egg """
        self.environment.install_feature("simple_example")
            
    def skip_simple_multiple_eggs(self, mockPuppet):
        """ The egg formula should install multiple eggs """
        m = Mock(spec=BuildoutPuppet)
        mockPuppet.return_value = m
        self.environment.install_feature("simple_multiple_eggs")
        assert m.eggs == ['jedi', 'epc==0.5', 'pelican']
        assert m.install.called

    def skip_simple_multiple_and_single_eggs(self, mockPuppet):
        """ The egg formula should install single and multiple eggs """
        m = Mock(spec=BuildoutPuppet)
        mockPuppet.return_value = m
        self.environment.install_feature("simple_multiple_and_single_eggs")
        assert sorted(m.eggs) == sorted(['jedi', 'epc==0.5', 'pelican', 'sprinter'])
        assert m.install.called

    def skip_sprinter(self, mockPuppet):
        """ The sprinter egg formula should install sprinter from a remote protocol """
        m = Mock(spec=BuildoutPuppet)
        mockPuppet.return_value = m
        self.environment.install_feature("sprinter")
        assert m.eggs == ['sprinter']
        assert m.links == ["http://github.com/toumorokoshi/sprinter/tarball/master#sprinter-0.6"]
        assert m.install.called
