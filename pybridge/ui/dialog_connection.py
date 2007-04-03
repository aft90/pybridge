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


import gtk
from wrapper import GladeWrapper

from pybridge.network.client import client
from manager import wm
from pybridge.ui import settings

TCP_PORT = 5040


class DialogConnection(GladeWrapper):

    glade_name = 'dialog_connection'


    def setUp(self):
        # Read connection parameters from client settings.

        connection = settings.connection
        if connection:
            self.entry_hostname.set_text(connection['hostname'])
            self.entry_portnum.set_text(connection['portnum'])
            self.entry_username.set_text(connection['username'])
            self.entry_password.set_text(connection['password'])
            self.check_savepassword.set_active(connection['password'] != '')
        else:
            self.entry_portnum.set_text(str(TCP_PORT))


    def connectSuccess(self, avatar):
        """Actions to perform when connecting succeeds."""

        # Save connection information.
        settings.connection = {}
        settings.connection['hostname'] = self.entry_hostname.get_text()
        settings.connection['portnum'] = self.entry_portnum.get_text()
        settings.connection['username'] = self.entry_username.get_text()
        if self.check_savepassword.get_active():
            settings.connection['password'] = self.entry_password.get_text()
        else:  # Flush password.
            settings.connection['password'] = ''

        wm.close(self)


    def connectFailure(self, failure):
        """Actions to perform when connecting fails."""
        error = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL,
                                 type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        error.set_markup(_('Could not connect to server.'))
        error.format_secondary_text(_('Reason: %s') % failure.getErrorMessage())
        error.run()
        error.destroy()
        self.button_connect.set_property('sensitive', True)


# Signal handlers.


    def on_dialog_connection_delete_event(self, widget, *args):
        wm.close(self)


    def on_field_changed(self, widget, *args):
        """Validates entry fields, disables Connect button if invalid."""
        # Host name, user name must not be blank.
        valid = self.entry_hostname.get_text() \
                and self.entry_username.get_text()
        # Port number must be an integer.
        if valid:
            try:
                port = int(self.entry_portnum.get_text())
            except ValueError:
                valid = False

        self.button_connect.set_property('sensitive', valid)


    def on_connect_clicked(self, widget, *args):
        # Prevent repeat clicks.
        self.button_connect.set_property('sensitive', False)

        hostname = self.entry_hostname.get_text()
        port = int(self.entry_portnum.get_text())
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


    def on_cancel_clicked(self, widget, *args):
        wm.close(self)

