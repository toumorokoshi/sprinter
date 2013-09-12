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
        # processor is a misnomer, it
        self.architecture = machine
        self.version = version
        self.dist = platform.dist()
        self.linux_distro, self.linux_version, self.linux_version_name = self.dist

    def isDebianBased(self):
        """ returns true if the system is debian based """
        return self.linux_distro.lower() in ['ubuntu', 'debian']

    def isFedoraBased(self):
        """ returns true if the system is fedora based """
        return self.linux_distro.lower() in ['centos', 'redhat', 'fedora']

    def isSUSEBased(self):
        """ returns true if the system is suse based """
        return self.linux_distro.lower() in ['suse']

    def isOSX(self):
        return self.system.lower() == "darwin"

    def isLinux(self):
        return self.system.lower() == "linux"

    def is64bit(self):
        return self.architecture == "x86_64"

    def operating_system(self):
        """ return the name of the operating system """
        return self.linux_distro or self.system

    def is_officially_supported(self):
        """
        Returns true if the current system is officially supported by
        sprinter
        """
        # TODO: Get the shell name and check that as well
        return self.isOSX() or self.isDebianBased()
