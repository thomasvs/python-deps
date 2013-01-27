# -*- Mode: Python; test-case-name: deps.test.test_distro -*-
# vi:si:et:sw=4:sts=4:ts=4

import os
import unittest

from deps import distro


class TestRelease(unittest.TestCase):
    def testGet(self):
        distro.getDistroFromRelease()

class TestAtLeast(unittest.TestCase):
    def testFedora(self):
        d = distro.Distro('fedora', 'Fedora Core', '5', 'i386')
        self.failUnless(d.atLeast('4test2'))
        self.failUnless(d.atLeast('5'))
        self.failIf(d.atLeast('5test2'))
        self.failIf(d.atLeast('40'))
        self.failIf(d.atLeast('50'))
