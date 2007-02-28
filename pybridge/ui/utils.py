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


import pybridge.environment as env

# Set up client with UI event handler.
from pybridge.network.client import client
from eventhandler import eventhandler
client.setEventHandler(eventhandler)

PORT = 5040  # Default port for PyBridge.




import ConfigParser


class Settings:
    """"""

    connection = {}
    general = {}


    def __init__(self, filename):
        self.config = ConfigParser.SafeConfigParser()
        self.filename = filename
        self.read()


    def read(self):
        """"""
        self.config.read(self.filename)
        
        # Create sections if they do not exist.
        for section in ('Connection', 'General'):
            if not self.config.has_section(section):
                self.config.add_section(section)
                self.write()
        
        for key, value in self.config.items('Connection'):
            self.connection[key] = value
        for key, value in self.config.items('General'):
            self.general[key] = value


    def write(self):
        """"""
        for key, value in self.connection.items():
            self.config.set('Connection', key, value)
        for key, value in self.general.items():
            self.config.set('General', key, value)
        self.config.write(file(self.filename, 'w'))


settings = Settings(env.find_config_client('client.cfg'))




import imp
from UserDict import UserDict


class WindowManager(UserDict):


    def open(self, windowname, parent=None):
        """Creates a new instance of a GladeWrapper window.
        
        @param windowname: the module name of the window.
        @param parent: if specified, a parent window to set transient property.
        """
        classname = ''.join([x.capitalize() for x in windowname.split('_')])
        exec("from %s import %s" % (windowname, classname))
        instance = eval(classname)(parent)
        self[windowname] = instance
        return instance


    def close(self, windowname, instance=None):
        """Closes an existing instance of a GladeWrapper window.
        
        @param windowname: the module name of the window.
        @param instance: if provided, the specific window object to close.
        """
        if instance or self.get(windowname):
            if instance is None:
                instance = self[windowname]
            instance.window.destroy()
            instance.cleanup()
            if self.get(windowname) == instance:
                del self[windowname]
            return True
        return False


windows = WindowManager()




import gtk
from twisted.internet import reactor


def quit():
    """Shutdown gracefully."""
    client.disconnect()
    settings.write()  # Save settings.
    reactor.stop()
    gtk.main_quit()

