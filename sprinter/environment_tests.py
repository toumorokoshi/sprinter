from __future__ import unicode_literals
import os
import shutil
import tempfile
from io import StringIO
from mock import Mock, call, patch
from nose import tools
from sprinter.testtools import (create_mock_environment,
                                create_mock_formulabase)
from sprinter.exceptions import SprinterException
from sprinter.environment import Environment
from sprinter.formulabase import FormulaBase
from sprinter.templates import source_template

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
        self.environment = create_mock_environment(
            source_config=source_config,
            target_config=target_config
        )
        self.environment.target.get_config = Mock()
        self.environment.grab_inputs()
        self.environment.target.get_config.assert_has_calls([
            call("password", default=None, secret=True, force_prompt=False),
            call("main_branch", default="comp_main", secret=True, force_prompt=False)
        ])
        assert self.environment.target.get_config.call_count == 2, "More calls were called!"

    def test_running_missing_formula(self):
        """ When a formula is missing, a sprinter exception should be thrown at the end """
        self.environment = create_mock_environment(
            target_config=missing_formula_config)
        try:
            self.environment.install()
            raise Exception("Exception not raised!")
        except SprinterException:
            pass

    def test_catch_exception_in_feature(self):
        """
        If an exception occurs in a feature, it should be caught
        and still allow other features to run
        """

    def test_feature_run_order_install(self):
        """ A feature install should have it's methods run in the proper order """
        environment = create_mock_environment(
            target_config=test_target
        )
        mock_formulabase = Mock(spec=FormulaBase)
        mock_formulabase.resolve.return_value = None
        mock_formulabase.validate.return_value = None
        mock_formulabase.prompt.return_value = None
        mock_formulabase.sync.return_value = None
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=mock_formulabase)
        environment.install()
        tools.eq_(mock_formulabase.method_calls, [call.should_run(),
                                                  call.validate(),
                                                  call.resolve(),
                                                  call.prompt(),
                                                  call.sync()])

    def test_feature_run_order_update(self):
        """ A feature update should have it's methods run in the proper order """
        environment = create_mock_environment(
            source_config=test_source,
            target_config=test_target,
            installed=True
        )
        mock_formulabase = Mock(spec=FormulaBase)
        mock_formulabase.resolve.return_value = None
        mock_formulabase.validate.return_value = None
        mock_formulabase.prompt.return_value = None
        mock_formulabase.sync.return_value = None
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=mock_formulabase)
        environment.update()
        tools.eq_(mock_formulabase.method_calls, [call.should_run(),
                                                  call.validate(),
                                                  call.resolve(),
                                                  call.prompt(),
                                                  call.sync()])

    def test_feature_run_order_remove(self):
        """ A feature remove should have it's methods run in the proper order """
        environment = create_mock_environment(
            source_config=test_source,
            installed=True
        )
        mock_formulabase = Mock(spec=FormulaBase)
        mock_formulabase.resolve.return_value = None
        mock_formulabase.validate.return_value = None
        mock_formulabase.prompt.return_value = None
        mock_formulabase.sync.return_value = None
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=mock_formulabase)
        environment.remove()
        tools.eq_(mock_formulabase.method_calls, [call.should_run(),
                                                  call.validate(),
                                                  call.resolve(),
                                                  call.prompt(),
                                                  call.sync()])

    def test_feature_run_order_deactivate(self):
        """ A feature deactivate should have it's methods run in the proper order """
        environment = create_mock_environment(
            source_config=test_source,
            installed=True
        )
        mock_formulabase = Mock(spec=FormulaBase)
        mock_formulabase.resolve.return_value = None
        mock_formulabase.validate.return_value = None
        mock_formulabase.prompt.return_value = None
        mock_formulabase.deactivate.return_value = None
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=mock_formulabase)
        environment.deactivate()
        tools.eq_(mock_formulabase.method_calls, [call.should_run(),
                                                  call.validate(),
                                                  call.resolve(),
                                                  call.prompt(),
                                                  call.deactivate()])

    def test_feature_run_order_activate(self):
        """ A feature should have it's methods run in the proper order """
        environment = create_mock_environment(
            source_config=test_source,
            installed=True
        )
        mock_formulabase = Mock(spec=FormulaBase)
        mock_formulabase.resolve.return_value = None
        mock_formulabase.validate.return_value = None
        mock_formulabase.prompt.return_value = None
        mock_formulabase.activate.return_value = None
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=mock_formulabase)
        environment.activate()
        tools.eq_(mock_formulabase.method_calls, [call.should_run(),
                                                  call.validate(),
                                                  call.resolve(),
                                                  call.prompt(),
                                                  call.activate()])

    def test_global_shell_configuration_bash(self):
        """ The global shell should dictate what files are injected (bash, gui, no zsh)"""
        # test bash, gui, no zshell
        global_shell_configuration_bash = """[shell]
bash = true
zsh = false
gui = true

[global]
env_source_rc = False
        """
        environment = create_mock_environment(
            target_config=test_target,
            global_config=global_shell_configuration_bash,
            mock_injections=False)
        environment.warmup()
        environment.injections.commit = Mock()
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=create_mock_formulabase())
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
        global_shell_configuration_bash = """[shell]
bash = true
zsh = true
gui = false

[global]
env_source_rc = True
        """
        environment = create_mock_environment(
            target_config=test_target,
            global_config=global_shell_configuration_bash,
            mock_injections=False,
            mock_global_injections=False)
        environment.warmup()
        environment.injections.commit = Mock()
        environment.global_injections.commit = Mock()
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=create_mock_formulabase())
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
        global_shell_configuration_zshell = """[shell]
bash = false
zsh = true
gui = false

[global]
env_source_rc = False
        """
        environment = create_mock_environment(
            target_config=test_target,
            global_config=global_shell_configuration_zshell,
            mock_injections=False)
        environment.warmup()
        environment.injections.commit = Mock()
        environment.formula_dict['sprinter.formulabase'] = Mock(return_value=create_mock_formulabase())
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
            env = Environment(root=temp_dir,
                              global_config="""[shell]
bash = false
zsh = true

[global]
env_source_rc = False
                              """)
            assert env.global_config.get('shell', 'bash') == "false"
            assert env.global_config.get('shell', 'zsh') == "true"
        finally:
            shutil.rmtree(temp_dir)

    def test_global_config_prompt(self):
        """ If no global config exists, it should prompt for the values it needs, and create a file """
        temp_dir = tempfile.mkdtemp()
        try:
            with patch('sprinter.lib.prompt') as prompt:
                prompt.return_value = "0"
                env = Environment(root=temp_dir)
                assert env.global_config.get('shell', 'bash') == "true"
                assert env.global_config.get('shell', 'zsh') == "true"
                assert env.global_config.get('shell', 'gui') == "true"
        finally:
            shutil.rmtree(temp_dir)

    def test_global_config_prompt_special_configs(self):
        """ If no global config exists, it should prompt for the values it needs, and create a file """
        temp_dir = tempfile.mkdtemp()
        try:
            with patch('sprinter.lib.prompt') as prompt:
                prompt.return_value = "2,3"
                env = Environment(root=temp_dir)
                assert env.global_config.get('shell', 'bash') == "false"
                assert env.global_config.get('shell', 'zsh') == "true"
                assert env.global_config.get('shell', 'gui') == "true"
        finally:
            shutil.rmtree(temp_dir)

    def test_utilssh_file_written(self):
        """ The latest utilssh file should be written at the end of an install """
        temp_dir = tempfile.mkdtemp()
        try:
            with patch('sprinter.lib.prompt') as prompt:
                prompt.return_value = "1,2"
                env = Environment(root=temp_dir)
                env.formula_dict['sprinter.formulabase'] = Mock(return_value=create_mock_formulabase())
                env.target = StringIO(test_target)
                env.warmup()
                env.injections.commit = Mock()
                env.install()
                global_path = os.path.join(temp_dir, '.global')
                assert os.path.exists(os.path.join(global_path, 'utils.sh'))
        finally:
            shutil.rmtree(temp_dir)
        

missing_formula_config = """
[missingformula]

[otherformula]
formula = sprinter.formulabase
"""

test_source = """
[testfeature]
formula = sprinter.formulabase
"""

test_target = """
[config]
namespace = testsprinter

[testfeature]
formula = sprinter.formulabase
"""
