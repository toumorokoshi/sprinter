"""
System encapsulates the retrieval of information about the system such
as:

* operating system
* debian, fedora, or os x based
"""

import platform
import re

debian_match = re.compile(".*(ubuntu|debian).*", re.IGNORECASE)
fedora_match = re.compile(".*(RHEL).*", re.IGNORECASE)


class System(object):

    def __init__(self, logger='sprinter'):
        (system, node, release, version, machine, processor) = platform.uname()
        self.system = system
        self.node = node
        self.processor = processor
        self.version = version
        self.processor = processor

    def isDebianBased(self):
        """ returns true if the system is debian based """
        return debian_match.match(self.version) is not None

    def isFedoraBased(self):
        """ returns true if the system is fedora based """
        return fedora_match.match(self.version) is not None

    def isOSX(self):
        return self.system.lower() == "darwin"

    def isLinux(self):
        return self.system.lower() == "linux"
