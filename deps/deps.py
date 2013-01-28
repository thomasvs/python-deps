# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# code to handle import errors and tell us more information about the
# missing dependency

import sys

from . import distro

class DependencyError(Exception):
    pass

class Dependency:

    module = None
    egg = None
    name = None
    homepage = None

    def install(self, distro):
        """
        Return an explanation on how to install the given dependency
        for the given distro/version/arch.

        @type  distro: L{distro.Distro}

        @rtype:   str or None
        @returns: an explanation on how to install the dependency, or None.
        """
        name = distro.distributor + '_install'
        m = getattr(self, name, None)
        if m:
            return m(distro)

    def validate(self):
        """
        Allow the dependency to validate itself, for example based on
        package version.

        @returns: None if ok, or an explanation of the problem if not.
        """
        pass

    # base methods that can be used by subclasses
    def Fedora_yum(self, packageName):
        """
        Returns a string explaining how to install the given package.
        """
        return "On Fedora, you can install %s with:\n" \
                "su -c \"yum install %s\"" % (self.module, packageName)

    def Debian_apt(self, packageName):
        """
        Returns a string explaining how to install the given package.
        """
        return "On Debian, you can install %s with:\n" \
                "sudo apt-get install %s" % (self.module, packageName)

    def Ubuntu_apt(self, packageName):
        """
        Returns a string explaining how to install the given package.
        """
        return "On Ubuntu, you can install %s with:\n" \
                "sudo apt-get install %s" % (self.module, packageName)

    # distro aliases
    def FedoraCore_install(self, distro):
        self.Fedora_install(distro)


    def version(self):
        return self.version_egg()

    def version_egg(self):
        if not self.egg:
            return None

        import pkg_resources
        return pkg_resources.get_distribution(self.egg).version


class DepsHandler(object):
    """
    I handle dependencies and related exceptions.
    """

    _deps = None

    def __init__(self, name):
        self._deps = {}
        self._name = name

    def add(self, dependency):
        self._deps[dependency.module] = dependency


    def validate(self):
        for dep in self._deps.values():
            ret = dep.validate()
            if ret:
                sys.stderr.write("Cannot use module '%s'\n" % dep.module)
                sys.stderr.write('This module is part of %s.\n' % dep.name)
                sys.stderr.write(ret + '\n')

                raise DependencyError(dep.module)


    def handleImportError(self, exception):
        """
        Handle dependency import errors by displaying more information about
        the dependency.
        """
        first = exception.args[0]
        if first.find('No module named ') < 0:
            raise
        module = first[len('No module named '):]
        module = module.split('.')[0]

        if module in self._deps.keys():
            dep = self._deps[module]
            sys.stderr.write("Could not import python module '%s'\n" % module)
            sys.stderr.write('This module is part of %s.\n' % dep.name)

            self.handleMissingDependency(dep)

            # how to confirm the python module got installed
            sys.stderr.write("\n")
            sys.stderr.write(
                'You can confirm it is installed by starting Python and running:\n')
            sys.stderr.write('import %s\n' % module)

            return

        # re-raise if we didn't have it
        raise

    def report(self, summary):
        raise NotImplementedError

    def handleMissingDependency(self, dep):
        if dep.homepage:
            sys.stderr.write('See %s for more information.\n\n' % dep.homepage)

        d = distro.getDistroFromRelease()
        if d:
            howto = dep.install(d)
            if howto:
                sys.stderr.write(howto)
            else:
                url = self.report('DEP: %s, %s' % (dep.module, d.description))
                sys.stderr.write("""On %s, %s does not know how to install %s.
    Please file a bug at:
    %s
    with instructions on how to install the dependency so we can add it.
    """ % (d.description, dep.module, self._name, url))
        else:
            url = self.report('DISTRO: Unknown')
            sys.stderr.write("""%s does not know your distribution.
    Please file a bug at:
    %s
    with instructions on how to recognize your distribution so we can add it.
    """ % (self._name, url))

        sys.stderr.write('\n')

        sys.stderr.write('Please install %s and try again.\n' % dep.module)
