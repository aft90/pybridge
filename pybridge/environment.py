# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2007 PyBridge Project.
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


import os
import sys


"""
This module provides path location services for PyBridge.

Note to PyBridge packagers:

The packaging policy of your distribution may specify a filesystem organisation
standard, which conflicts with the directory structure defined in this module.

This is the only module that you should need to modify to make PyBridge
compliant with distribution policy.
"""


# Locate base directory.
if hasattr(sys, 'frozen'):  # If py2exe distribution.
    currentdir = os.path.dirname(sys.executable)
    basedir = os.path.abspath(currentdir)
else:  # Typically /usr/ (if installed) or root of source distribution.
    currentdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    basedir = os.path.normpath(os.path.join(currentdir, '..'))

# Locate shared resources directory, typically /usr/share/.
if os.path.exists(os.path.join(basedir, 'share')):
    sharedir = os.path.join(basedir, 'share')
else:  # Root of source distribution.
    sharedir = basedir

# Locate client configuration directory, typically ~/.pybridge/.
clientconfigdir = os.path.join(os.path.expanduser('~'), '.pybridge')
if not os.path.exists(clientconfigdir):
    os.mkdir(clientconfigdir)  # Create directory.

# Locate server configuration directory.
serverconfigdir = clientconfigdir


def find_config_client(name):
    """A client configuration file is located in:
    
    <clientconfigdir>/
    """
    return os.path.join(clientconfigdir, name)


def find_config_server(name):
    """A server configuration file is located in:

    <serverconfigdir>/
    """
    return os.path.join(serverconfigdir, name)


def find_doc(name):
    """A documentation file may be located in:
    
    <sharedir>/doc/pybridge/ (installed)
    <basedir>/               (source)
    """
    if sharedir == basedir:
        return os.path.join(basedir, name)
    else:
        return os.path.join(sharedir, 'doc', 'pybridge', name)


def find_glade(name):
    """A Glade interface file may be located in:
    
    <sharedir>/pybridge/glade/ (installed)
    <basedir>/glade/           (source)
    """
    if sharedir == basedir:
        return os.path.join(basedir, 'glade', name)
    else:
        return os.path.join(sharedir, 'pybridge', 'glade', name)


def find_pixmap(name):
    """A pixmap file may be located in:
    
    <sharedir>/pybridge/pixmaps/ (installed)
    <basedir>/pixmaps/           (source)
    """
    if sharedir == basedir:
        return os.path.join(basedir, 'pixmaps', name)
    else:
        return os.path.join(sharedir, 'pybridge', 'pixmaps', name)


def get_localedir():
    """Returns the path of the locale directory."""
    return os.path.join(sharedir, 'locale')

