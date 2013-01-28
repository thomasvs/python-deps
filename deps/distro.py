# -*- Mode: Python; test-case-name: test.test_distro -*-
# vi:si:et:sw=4:sts=4:ts=4

import commands
import os

import distutils.version

"""
Figure out what distribution, architecture and version the user is on.
"""

class DistroException(Exception):
    pass

class Distro:
    """
    @cvar description: a longer human-readable name for the distro
    @type description: str
    @cvar distributor: a short lower-case identifier for the distro
    @type distributor: str
    @cvar release:     the version of the distro
    @type release:     str
    @cvar arch:        the architecture of the distro
    @type arch:        str
    """
    description = None
    distributor = None
    release = None
    arch = None

    def __init__(self, description, distributor, release, arch):
        self.description = description
        self.distributor = distributor
        self.release = release
        self.arch = arch

    def atLeast(self, release):
        """
        @param release: release to compare with
        @type  release: str

        Returns: whether the distro is at least as new as the given release,
                 taking non-numbers into account.
        """
        mine = distutils.version.LooseVersion(self.release)
        theirs = distutils.version.LooseVersion(release)
        return mine >= theirs

def getSysName():
    """
    Get the system name.  Typically the first item in the os.uname tuple.
    """
    return os.uname()[1]

def getMachine():
    """
    Get the machine architecture.  Typically the fifth item in os.uname.
    """
    return os.uname()[4]

def getDistroFromRelease():
    """
    Decide on the distro based on the presence of a distro-specific release
    file.

    rtype: L{Distro} or None.
    """
    # start with lsb_release
    (status, output) = commands.getstatusoutput("lsb_release -i")
    if os.WIFEXITED(status):
        ret = os.WEXITSTATUS(status)
        if ret == 127:
            raise DistroException('lsb_release binary not found')

    if output and output.startswith('Distributor ID:'):
        distributor = output.split(':', 2)[1].strip()
        output = commands.getoutput("lsb_release -d")
        description = output.split(':', 2)[1].strip()
        output = commands.getoutput("lsb_release -r")
        release = output.split(':', 2)[1].strip()

        return Distro(description, distributor, release, None)
