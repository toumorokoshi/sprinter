import os


def test_link_dir_link(tmpdir, link_dir):
    test_file = tmpdir.join("test")
    test_file.write("foo")
    link_dir.link(test_file.strpath, "target")
    assert os.path.islink(
        os.path.join(link_dir.root, "target")
    )


def test_link_dir_remove(tmpdir, link_dir):
    test_file = tmpdir.join("test")
    test_file.write("foo")
    link_dir.link(test_file.strpath, "target")
    link_dir.remove("target")
    assert not os.path.exists(
        os.path.join(link_dir.root, "target")
    )


def test_link_dir_rooted_created(tmpdir, link_dir):
    """ root should be created, when a link is requested ."""
    assert not os.path.exists(link_dir._root)
    assert os.path.exists(link_dir.root)
