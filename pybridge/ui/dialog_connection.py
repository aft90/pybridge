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

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import gtk
from wrapper import GladeWrapper

from pybridge.network.client import client
from pybridge.conf import TCP_PORT
import utils


class DialogConnection(GladeWrapper):

    glade_name = 'dialog_connection'


    def new(self):
        # Read connection parameters from client settings.
        hostname = utils.settings.connection.get('hostname', '')
        username = utils.settings.connection.get('username', '')
        password = utils.settings.connection.get('password', '')
        
        self.entry_hostname.set_text(hostname)
        self.entry_username.set_text(username)
        self.entry_password.set_text(password)
        if password:
            self.check_savepassword.set_active(True)


    def connectSuccess(self, avatar):
        """Actions to perform when connecting succeeds."""
        hostname = self.entry_hostname.get_text()
        username = self.entry_username.get_text()
        if self.check_savepassword.get_active():
            password = self.entry_password.get_text()
        else:  # Flush password.
            password = ''
        
        # Save connection information.
        utils.settings.connection['hostname'] = hostname
        utils.settings.connection['username'] = username
        utils.settings.connection['password'] = password
        
        # Launch main window.
        utils.windows.close('dialog_connection')
        utils.windows.open('window_main')


    def connectFailure(self, failure):
        """Actions to perform when connecting fails."""
        error = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL,
                                 type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        error.set_markup("Could not connect to server.")
        error.format_secondary_text("Reason: %s" % failure.getErrorMessage())
        error.run()
        error.destroy()
        self.button_connect.set_property('sensitive', True)


# Signal handlers.


    def on_dialog_connection_delete_event(self, widget, *args):
        utils.quit()


    def on_hostname_changed(self, widget, *args):
        sensitive = self.entry_hostname.get_text() != "" and self.entry_username.get_text() != ""
        self.button_connect.set_property('sensitive', sensitive)


    def on_username_changed(self, widget, *args):
        self.on_hostname_changed(self, widget, *args)  # Same as host field.


    def on_connect_clicked(self, widget, *args):
        self.button_connect.set_property('sensitive', False)  # Prevent repeat clicks.
        
        hostname = self.entry_hostname.get_text()
        port = TCP_PORT
        client.connect(hostname, port)
        
        username = self.entry_username.get_text()
        password = self.entry_password.get_text()
        register = self.check_registeruser.get_active() == True
        
        if register:
            # Attempt login only after registration.
            # TODO: can defer.waitForDeferred() be used here?
            d = client.register(username, password)
            d.addCallback(lambda _: client.login(username, password))
        else:
            d = client.login(username, password)
        d.addCallbacks(self.connectSuccess, self.connectFailure)


    def on_quit_clicked(self, widget, *args):
        utils.quit()

