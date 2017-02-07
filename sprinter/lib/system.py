"""
System encapsulates the retrieval of information about the system such
as:

* operating system
* debian, fedora, or os x based
"""
from __future__ import unicode_literals
import platform
import re

debian_match = re.compile(".*(ubuntu|debian).*", re.IGNORECASE)
fedora_match = re.compile(".*(RHEL).*", re.IGNORECASE)

SYSTEM, NODE, RELEASE, VERSION, ARCHITECTURE, PROCESSOR = platform.uname()
LINUX_DISTRO, LINUX_VERSION, LINUX_VERSION_NAME = platform.dist()

def get_system_info():
    """ return the system info as a string """
    return (
        "operating system = " + operating_system() + "\n" +
        "is officially supported = " + str(is_officially_supported()) + "\n" +
        "node = "   + NODE + "\n" +
        "release = " + RELEASE + "\n" +
        "version = " + VERSION + "\n" +
        "architecture = " + ARCHITECTURE + "\n"
    )


def is_arch():
    return 'arch' in RELEASE.lower()


def is_debian():
    """ returns true if the system is debian based """
    return LINUX_DISTRO.lower() in ['ubuntu', 'debian', 'linuxmint']


def is_fedora():
    """ returns true if the system is fedora based """
    return LINUX_DISTRO.lower() in ['centos', 'redhat', 'fedora']


def is_suse():
    """ returns true if the system is suse based """
    return LINUX_DISTRO.lower() in ['suse']


def is_osx():
    return SYSTEM.lower() == "darwin"


def is_linux():
    return SYSTEM.lower() == "linux"


def is_64_bit():
    return ARCHITECTURE == "x86_64"


def operating_system():
    """ return the name of the operating system """
    return LINUX_DISTRO or SYSTEM


def is_officially_supported():
    """
    Returns true if the current system is officially supported by
    sprinter
    """
    # TODO: Get the shell name and check that as well
    return is_osx() or is_debian() or is_arch()
