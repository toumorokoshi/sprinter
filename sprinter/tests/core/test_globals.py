from sprinter.core.globals import load_global_config
from mock import patch

CFG = """
[global]
env_source_rc = True

[shell]
bash = true
gui = true
zsh = true
""".strip()


def test_no_prompt_on_config_exists(tmpdir):
    path_object = tmpdir.join("config.cfg")
    path_str = path_object.strpath
    with path_object.open(ensure=True, mode="w+") as fh:
        fh.write(CFG)
    with patch("sprinter.lib.prompt", return_value=0) as prompt:
        load_global_config(path_str)
        assert not prompt.called
