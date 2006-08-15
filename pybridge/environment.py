# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2006 PyBridge Project.
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


class Environment:
    """This module provides path location services for PyBridge."""


    def __init__(self):
        # Locate base directory.
        if hasattr(sys, 'frozen'):  # If py2exe distribution.
            currentdir = os.path.dirname(sys.executable)
            self.basedir = os.path.abspath(currentdir)
        else:  # Typically /usr/ or root of source distribution.
            currentdir = os.path.dirname(os.path.abspath(sys.argv[0]))
            self.basedir = os.path.normpath(os.path.join(currentdir, '..'))
        
        # Locate shared resources directory, typically /usr/share/.
        if os.path.exists(os.path.join(self.basedir, 'share')):
            self.sharedir = os.path.join(self.basedir, 'share')
        else:  # Root of source distribution.
            self.sharedir = self.basedir
        
        # Locate config directory.
        self.configdir = os.path.join(os.path.expanduser('~'), '.pybridge')
        if not os.path.exists(self.configdir):
            os.mkdir(self.configdir)  # Create directory.


    def find_configfile(self, name):
        """A config file is located in <configdir>/"""
        return os.path.join(self.configdir, name)


    def find_doc(self, name):
        """A documentation file may be located in:
        
        <sharedir>/doc/pybridge/ (installed)
        <basedir>/               (source)
        """
        if self.sharedir == self.basedir:
            return os.path.join(self.basedir, name)
        else:
            return os.path.join(self.sharedir, 'doc', 'pybridge', name)


    def find_glade(self, name):
        """A Glade interface file may be located in:
        
        <sharedir>/pybridge/glade/ (installed)
        <basedir>/glade/           (source)
        """
        if self.sharedir == self.basedir:
            return os.path.join(self.basedir, 'glade', name)
        else:
            return os.path.join(self.sharedir, 'pybridge', 'glade', name)


    def find_pixmap(self, name):
        """A pixmap file may be located in:
        
        <sharedir>/pybridge/pixmaps/ (installed)
        <basedir>/pixmaps/           (source)
        """
        if self.sharedir == self.basedir:
            return os.path.join(self.basedir, 'pixmaps', name)
        else:
            return os.path.join(self.sharedir, 'pybridge', 'pixmaps', name)


    def get_localedir(self):
        """Returns the path of the locale directory."""
        return os.path.join(self.sharedir, 'locale')


environment = Environment()

