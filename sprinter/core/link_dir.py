import logging
import os

LOG = logging.getLogger(__name__)


class LinkDirException(Exception):
    pass


class LinkDir(object):
    """
    represents a directory to symlink things from and to.
    """
    def __init__(self, root):
        self._root = root

    def link(self, source, name):
        """
        Symlink an object at path to name in the dir_name folder. remove
        it if it already exists.
        """
        self.remove(name)

        target = os.path.join(self.root, name)
        LOG.debug("Attempting to symlink {0} to {1}...".format(source, target))

        if os.path.islink(target):
            os.remove(target)

        if os.path.exists(target):
            raise LinkDirException("{0} is not a symlink. unable to safely replace with a symlink.".format(target))
        os.symlink(source, target)

    def remove(self, name):
        target = os.path.join(self.root, name)
        if os.path.islink(target):
            os.remove(target)
        pass

    @property
    def root(self):
        if not os.path.exists(self._root):
            os.makedirs(self._root)
        elif not os.path.isdir(self._root):
            raise LinkDirException(
                "unable to symlink into non-directory: {0}".format(self._root)
            )
        return self._root
