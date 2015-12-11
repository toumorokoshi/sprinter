class Sprinter(object):

    def __init__(self, root):
        # typically, the root is the user's
        # home directory.
        self._root = root

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
        pass
