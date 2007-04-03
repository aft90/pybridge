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


import gettext
import gtk
import gtk.glade
import sys

import pybridge.environment as env

GLADE_PATH = env.find_glade("pybridge.glade")
if sys.platform == 'win32':  # Win32 should use the ICO icon.
    ICON_PATH = env.find_pixmap("pybridge.ico")
else:  # All other platforms should use the PNG icon.
    ICON_PATH = env.find_pixmap("pybridge.png")


class GladeWrapper(object):
    """A superclass for Glade-based application windows.
    
    Modified from: http://www.pixelbeat.org/libs/libglade.py
    """

    def __init__(self, parent=None):
        """Initialise window from Glade definition.
        
        @param parent: pointer to parent gtk.Window, or None.
        """
        self.widgets = gtk.glade.XML(GLADE_PATH, self.glade_name,
                                     gettext.textdomain())
        self.window = self.widgets.get_widget(self.glade_name)

        instance_attributes = {}
        for attribute in dir(self.__class__):
            instance_attributes[attribute] = getattr(self, attribute)
        self.widgets.signal_autoconnect(instance_attributes)

        self.window.set_icon_from_file(ICON_PATH)
        if parent is not None:
            self.window.set_transient_for(parent.window)

        self.setUp()


    def __getattr__(self, attribute):
        """Allows referencing of Glade widgets as window attributes."""
        widget = self.widgets.get_widget(attribute)
        if widget is None:
            raise AttributeError("No widget named %s" % attribute)
        self.__dict__[attribute] = widget  # Cache reference for later.
        return widget


    def setUp(self):
        """Override this method to run code when this window is created."""
        pass


    def tearDown(self):
        """Override this method to run code when this window is destroyed."""
        pass

