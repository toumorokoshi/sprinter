import os
from .state import SprinterState

class Sprinter(object):

    def __init__(self, root, state_file="state.yaml"):
        # typically, the root is the user's
        # home directory.
        self._root = root
        self._state = SprinterState.load(os.path.join(root, state_file))

    def install(self, package_source):
        pass

    def update(self, package_name):
        pass

    def remove(self, package_name):
        pass

    def deactivate(self, package_name):
        pass

    def activate(self, package_name):
        pass

    def packages(self):
        return self._state.packages
        pass

    def _save(self):
        pass

    def _load(self, root):
        pass
