from __future__ import unicode_literals
import os
import shutil
import tempfile
from mock import Mock, call, patch
from nose import tools
from nose.tools import eq_, raises, ok_
from sprinter.testtools import (MockEnvironment,
                                create_mock_formulabase)
from sprinter.exceptions import SprinterException, FormulaException
from sprinter.environment import Environment
from sprinter.core.templates import source_template
from sprinter.core.globals import create_default_config

source_config = """
[config]
test = hi
"""

target_config = """
[config]
inputs = password?
         main_branch?==comp_main

[noformula]
blank = thishasnoformula
"""


class TestEnvironment(object):
    """ Tests for the environment """

    def test_grab_inputs_existing_source(self):
        """ Grabbing inputs should source from source first, if it exists """

        with MockEnvironment(source_config, target_config) as environment:
            environment.target.grab_inputs = Mock()
            environment.grab_inputs()
            eq_(environment.target.inputs.get_unset_inputs(), set(['password', 'main_branch']))

    @tools.raises(SprinterException)
    def test_running_missing_formula(self):
        """ When a formula is missing, a sprinter exception should be thrown at the end """
        with MockEnvironment(target_config=missing_formula_config) as environment:
            environment.install()

    def test_catch_exception_in_feature(self):
        """
        If an exception occurs in a feature, it should be caught
        and still allow other features to run
        """

    def test_feature_run_order_install(self):
        """ A feature install should have it's methods run in the proper order """
        with patch('sprinter.formula.base.FormulaBase', new=create_mock_formulabase()) as formulabase:
            with MockEnvironment(test_source, test_target, mock_formulabase=formulabase) as environment:
                environment.install()
                eq_(formulabase().method_calls, [call.should_run(),
                                                 call.validate(),
                                                 call.resolve(),
                                                 call.prompt(),
                                                 call.sync()])

    def test_feature_run_order_update(self):
        """ A feature update should have it's methods run in the proper order """
        with patch('sprinter.formula.base.FormulaBase', new=create_mock_formulabase()) as formulabase:
            with MockEnvironment(test_source, test_target, mock_formulabase=formulabase) as environment:
                environment.directory = Mock(spec=environment.directory)
                environment.directory.root_dir = "/tmp/"
                environment.directory.new = False
                environment.update()
                eq_(formulabase().method_calls, [call.should_run(),
                                                 call.validate(),
                                                 call.resolve(),
                                                 call.prompt(),
                                                 call.sync()])

    def test_feature_run_order_remove(self):
        """ A feature remove should have it's methods run in the proper order """
        with patch('sprinter.formula.base.FormulaBase', new=create_mock_formulabase()) as formulabase:
            with MockEnvironment(test_source, test_target, mock_formulabase=formulabase) as environment:
                environment.directory = Mock(spec=environment.directory)
                environment.directory.new = False
                environment.remove()
                eq_(formulabase().method_calls, [call.should_run(),
                                                 call.validate(),
                                                 call.resolve(),
                                                 call.prompt(),
                                                 call.sync()])

    def test_feature_run_order_deactivate(self):
        """ A feature deactivate should have it's methods run in the proper order """
        with patch('sprinter.formula.base.FormulaBase', new=create_mock_formulabase()) as formulabase:
            with MockEnvironment(test_source, test_target, mock_formulabase=formulabase) as environment:
                environment.directory = Mock(spec=environment.directory)
                environment.directory.new = False
                environment.deactivate()
                eq_(formulabase().method_calls, [call.should_run(),
                                                 call.validate(),
                                                 call.resolve(),
                                                 call.prompt(),
                                                 call.deactivate()])

    def test_feature_run_order_activate(self):
        """ A feature should have it's methods run in the proper order """
        with patch('sprinter.formula.base.FormulaBase', new=create_mock_formulabase()) as formulabase:
            with MockEnvironment(test_source, test_target, mock_formulabase=formulabase) as environment:
                environment.directory = Mock(spec=environment.directory)
                environment.directory.root_dir = "/tmp/"
                environment.directory.new = False
                environment.activate()
                eq_(formulabase().method_calls, [call.should_run(),
                                                 call.validate(),
                                                 call.resolve(),
                                                 call.prompt(),
                                                 call.activate()])

    def test_global_shell_configuration_bash(self):
        """ The global shell should dictate what files are injected (bash, gui, no zsh)"""
        # test bash, gui, no zshell
        global_config = create_default_config()
        global_config.set('shell', 'bash', 'true')
        global_config.set('shell', 'zsh', 'false')
        global_config.set('shell', 'gui', 'true')
        with MockEnvironment(test_source, test_target, global_config=global_config) as environment:
            environment.install()
            assert [x for x in environment.injections.inject_dict.keys() if x.endswith('.bashrc')]
            env_injected = False
            for profile in ['.bash_profile', '.bash_login', '.profile']:
                env_injected = env_injected or filter(lambda x: x.endswith(profile), environment.injections.inject_dict.keys())
            assert env_injected
            assert not [x for x in environment.injections.inject_dict.keys() if x.endswith('.zshrc')]
            for profile in ['.zprofile', '.zlogin']:
                assert not [x for x in environment.injections.inject_dict.keys() if x.endswith(profile)]

    def test_env_to_rc_injection(self):
        """ If env_source_rc is set to true, the env environments should source the rc """
        # test bash, gui, no zshell
        global_config = create_default_config()
        global_config.set('global', 'env_source_rc', True)
        with MockEnvironment(test_source, test_target, global_config=global_config) as environment:
            environment.install()

            # bash
            env_injected = False
            full_rc_path = os.path.expanduser(os.path.join("~", ".bashrc"))
            for profile in ['.bash_profile', '.bash_login', '.profile']:
                full_profile_path = os.path.expanduser(os.path.join("~", profile))
                specific_env_injected = full_profile_path in environment.global_injections.inject_dict
                if specific_env_injected:
                    env_injected = True
                    assert (source_template % (full_rc_path, full_rc_path) in
                            environment.global_injections.inject_dict[full_profile_path])
            assert env_injected

            # zshell
            env_injected = False
            full_rc_path = os.path.expanduser(os.path.join("~", ".zshrc"))
            for profile in ['.zprofile', '.zlogin']:
                full_profile_path = os.path.expanduser(os.path.join("~", profile))
                specific_env_injected = full_profile_path in environment.global_injections.inject_dict
                if specific_env_injected:
                    env_injected = True
                    assert (source_template % (full_rc_path, full_rc_path) in
                            environment.global_injections.inject_dict[full_profile_path])
            assert env_injected

    def test_global_shell_configuration_zshell(self):
        """ The global shell should dictate what files are injected (zsh, no bash, no gui)"""
        # test zshell, no bash, no gui
        global_config = create_default_config()
        global_config.set('shell', 'bash', 'false')
        global_config.set('shell', 'zsh', 'true')
        global_config.set('shell', 'gui', 'false')
        with MockEnvironment(target_config=test_target, global_config=global_config) as environment:
            environment.install()

            assert [x for x in environment.injections.inject_dict.keys() if x.endswith('.zshrc')]

            env_injected = False
            for profile in ['.zprofile', '.zlogin']:
                env_injected = env_injected or filter(lambda x: x.endswith(profile), environment.injections.inject_dict.keys())
            assert env_injected

            assert not [x for x in environment.injections.inject_dict.keys() if x.endswith('.bashrc')]

            for profile in ['.bash_profile', '.bash_login']:
                assert not [x for x in environment.injections.inject_dict.keys() if x.endswith(profile)]

    def test_global_config(self):
        """ Global config should accept a file-like object, or default to ROOT/.sprinter/.global/config.cfg """
        temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(temp_dir, ".global"))
        with open(os.path.join(temp_dir, ".global", "config.cfg"), 'w+') as fh:
            fh.write("""[shell]
bash = true

[global]
env_source_rc = False
            """)
        try:
            env = Environment(root=temp_dir)
            assert env.global_config.get('shell', 'bash') == "true"
        finally:
            shutil.rmtree(temp_dir)

    def test_utilssh_file_written(self):
        """ The latest utilssh file should be written at the end of an install """
        with MockEnvironment(target_config=test_target) as environment:
            environment.install()
            assert os.path.exists(os.path.join(environment.global_path, 'utils.sh'))

    def test_message_failure_bad_manifest(self):
        "On an environment with a incorrectly formatted manifest, message_failure should return None"""
        with MockEnvironment(target_config=test_target) as environment:
            environment.target = "gibberish"
            assert environment.message_failure() is None

    @raises(SprinterException)
    def test_no_namespace(self):
        """ an warmup should fail if the namespace is not set and cant' be determined implicitely """
        with MockEnvironment(target_config="") as environment:
            del(environment.namespace)
            environment.warmup()

    def test_grab_inputs_in_install(self):
        """ an install should grab all required inputs at the beginning """
        with MockEnvironment(test_source, test_target) as environment:
            environment.grab_inputs = Mock()
            environment.install()
            ok_(environment.grab_inputs.called)

    def test_source_to_target_config(self):
        """ On an update, values in the config section should be preserved """
        with MockEnvironment(test_input_source, test_input_target) as environment:
            environment.directory = Mock(spec=environment.directory)
            environment.directory.root_dir = "/tmp/"
            environment.directory.new = False
            environment.update()
            eq_(environment.target.get('config', 'my_custom_value'), 'foo')
            eq_(environment.target.get('config', 'non_custom_value'), 'baz')

    @raises(SprinterException)
    def test_errors_fail_out_immediately(self):
        """ Failures in the update should fail out right then and there,
            not afterward.
            See https://github.com/toumorokoshi/sprinter/issues/56
        """

        with patch('sprinter.formula.base.FormulaBase', new=create_mock_formulabase()) as formulabase:
            formulabase.install.side_effect = Exception
            with MockEnvironment(None, test_target, mock_formulabase=formulabase) as environment:
                environment.run_feature('testfeature', 'install')

    def test_feature_run_remove_failure(self):
        """ A feature remove should not throw SprinterException on failure - it should
            raise a FeatureException that is handle in remove() """

        with patch('sprinter.formula.base.FormulaBase', new=create_mock_formulabase()) as formulabase:
            formulabase.sync.side_effect = Exception
            with MockEnvironment(test_source, test_target, mock_formulabase=formulabase) as environment:
                environment.directory = Mock(spec=environment.directory)
                environment.directory.new = False
                environment.remove()


missing_formula_config = """
[missingformula]

[otherformula]
formula = sprinter.formula.base
"""

test_source = """
[testfeature]
formula = sprinter.formula.base
"""

test_target = """
[config]
namespace = testsprinter

[testfeature]
formula = sprinter.formula.base
"""

test_input_source = """
[config]
namespace = testsprinter
my_custom_value = foo
"""

test_input_target = """
[config]
namespace = testsprinter
my_custom_value = bar
non_custom_value = baz
"""
