import os
from .core.directory import Directory
from .core.injections import Injections
from .core.link_dir import LinkDir


class Environment2(object):

    def __init__(self, name, root, source=None, target=None,
                 sprinter_namespace="SPRINTER",
                 INJECTION_OVERRIDE="SPRINTER_OVERRIDES"):
        self._root = root
        self.source = source
        self.target = target
        self.bin = LinkDir(os.path.join(self._root, "bin"))
        self.lib = LinkDir(os.path.join(self._root, "lib"))
        self.injections = Injections(
            wrapper="{0}_{1}".format(self._sprinter_namespace, name),
            override=self._injection_override
        )
        # TODO: get a shell util path
        self.directory = Directory(self._root)
