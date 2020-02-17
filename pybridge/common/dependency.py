# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2009 PyBridge Project.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


"""
This module provides a dependency checking service for PyBridge.

Note to PyBridge packagers:
    Most package management systems provide a facility for packages to specify
    required dependencies. It is unnecessary to duplicate this functionality,
    so you may remove this module from PyBridge, together with its references
    in bin/pybridge and bin/pybridge-server.
"""


PYTHON_REQUIRED = (2, 5)
CONFIGOBJ_REQUIRED = (4,0)
PYCAIRO_REQUIRED = (1,4)
PYGTK_REQUIRED = '2.0'
SQLOBJECT_REQUIRED = '0.9'
TWISTED_REQUIRED = (2,5)
ZOPE_REQUIRED = '3.0'


"""Verifies that all libraries required by PyBridge client are available."""
def verify_pybridge():
    check_python()
    check_pygtk()
    check_pycairo()
    check_twisted()
    check_configobj()
    check_zope()


"""Verifies that all libraries required by PyBridge server are available."""
def verify_pybridge_server():
    check_python()
    check_sqlobject()
    check_twisted()
    check_configobj()
    check_zope()


def dependency_check(dependency, required, installed=None):
    if type(required) is tuple and type(installed) is str:
        installed = tuple(map(type(required[0]), installed.split('.')))
    if installed and installed >= required:
        return  # Success condition

    error = "PyBridge could not start, because a required library is not available:"

    error += "\n\t%(dependency)s -- %(req)s (or newer) required, %(inst)s installed" % \
             {'dependency': dependency, 'req': required, 'inst': installed or "not"}

    raise SystemExit(error)


#
# Version checkers
#


def check_python():
    import sys
    PYTHON_INSTALLED = sys.version_info[:2]
    dependency_check("Python", PYTHON_REQUIRED, PYTHON_INSTALLED)


def check_pycairo():
    PYCAIRO_INSTALLED = None
    try:
        import cairo
        PYCAIRO_INSTALLED = cairo.cairo_version_string()
    except ImportError:
        pass
    finally:
        dependency_check("PyCairo", PYCAIRO_REQUIRED, PYCAIRO_INSTALLED)


def check_configobj():
    CONFIGOBJ_INSTALLED = None
    try:
        from configobj import __version__ as CONFIGOBJ_INSTALLED
    except ImportError:
        pass
    finally:
        dependency_check("ConfigObj", CONFIGOBJ_REQUIRED, CONFIGOBJ_INSTALLED)


def check_pygtk():
    try:
        import pygtk
        pygtk.require(PYGTK_REQUIRED)
    except AssertionError as ImportError:
        dependency_check("PyGTK", PYGTK_REQUIRED)


def check_sqlobject():
    try:
        import sqlobject
        # TODO: check SQLObject version
    except ImportError:
        dependency_check("SQLObject", SQLOBJECT_REQUIRED)


def check_twisted():
    TWISTED_INSTALLED = None
    try:
        from twisted.copyright import version as TWISTED_INSTALLED
    except ImportError:
        pass
    finally:
        dependency_check("Twisted Core", TWISTED_REQUIRED, TWISTED_INSTALLED)


def check_zope():
    try:
        import zope.interface
        # TODO: check Zope Interface version
    except ImportError:
        dependency_check("Zope Interface", ZOPE_REQUIRED)

