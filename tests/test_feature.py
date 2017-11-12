from sprinter.core import Manifest

def test_feature_executes_rc_env(directory, feature):
    """
    during an update, feature should execute injection
    into rc and env
    """
    feature.instance.source = Manifest.from_dict({
        "foo": {"rc": "old"}
    }).get_feature_config("foo")
    feature.instance.target = Manifest.from_dict({
        "foo": {"rc": "bar"}
    }).get_feature_config("foo")
    feature.sync()
    directory.rc_file.seek(0)
    assert "bar" in directory.rc_file.read()
