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
from config import config
from manager import wm

TCP_PORT = 5040


class DialogConnection(GladeWrapper):

    glade_name = 'dialog_connection'


    def setUp(self):
        # Read connection parameters from client settings.

        connection = config['Connection']
        if connection:
            self.entry_hostname.set_text(connection.get('HostAddress', 'localhost'))
            self.entry_portnum.set_text(str(connection.get('PortNumber', TCP_PORT)))
            self.entry_username.set_text(connection.get('Username', ''))
            password = connection.get('Password', '').decode('rot13')
            self.entry_password.set_text(password)
            self.check_savepassword.set_active(password != '')
        else:
            self.entry_portnum.set_text(str(TCP_PORT))


    def connectSuccess(self, avatar):
        """Actions to perform when connecting succeeds."""

        # Save connection information.
        connection = config['Connection']
        connection['HostAddress'] = self.entry_hostname.get_text()
        connection['PortNumber'] = int(self.entry_portnum.get_text())
        connection['Username'] = self.entry_username.get_text()
        if self.check_savepassword.get_active():
            # Encode password, to confuse password sniffer software.
            # ROT13 encoding does *not* provide security!
            password = self.entry_password.get_text().encode('rot13')
        else:
            password = ''  # Flush password.
        connection['Password'] = password

        wm.close(self)


    def connectFailure(self, failure):
        """Actions to perform when connecting fails."""
        client.disconnect()

        dialog = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL,
                               type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        dialog.set_title(_('Connection failed'))
        dialog.set_markup(_('Could not connect to server.'))
        dialog.format_secondary_text(_('Reason: %s') % failure.getErrorMessage())

        def dialog_response_cb(dialog, response_id):
            dialog.destroy()
            self.button_connect.set_property('sensitive', True)

        dialog.connect('response', dialog_response_cb)
        dialog.show()


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

