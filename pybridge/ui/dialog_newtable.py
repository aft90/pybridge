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


from gi.repository import Gtk
from .wrapper import GladeWrapper

from pybridge.network.client import client
from pybridge.games import SUPPORTED_GAMES
from .manager import wm

# TODO: import all Window*Table classes automatically.
from pybridge.games.bridge.ui.window_bridgetable import WindowBridgeTable


class DialogNewtable(GladeWrapper):

    glade_name = 'dialog_newtable'


    def setUp(self):
        # Build and populate list of supported games.
        model = Gtk.ListStore(str)
        self.gamelist.set_model(model)
        cell = Gtk.CellRendererText()
        self.gamelist.pack_start(cell, True)
        self.gamelist.add_attribute(cell, 'text', 0)

        for gamename in sorted(SUPPORTED_GAMES):
            iter = model.append((gamename, ))
        self.gamelist.set_active_iter(iter)
        # TODO: display intersection of games supported by client and server.


    def createSuccess(self, table):
        wm.close(self)
        # TODO: select correct table window class.
        window = wm.open(WindowBridgeTable, id=table.id)
        window.setTable(table)


    def createFailure(self, reason):
        error = reason.getErrorMessage()
        dialog = Gtk.MessageDialog(parent=self.window, flags=Gtk.DialogFlags.MODAL,
                                type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK)
        dialog.set_title(_('Could not create table'))
        dialog.set_markup(_('The table was not created by the server.'))
        dialog.format_secondary_text(_('Reason: %s') % error)

        def dialog_response_cb(dialog, response_id):
            dialog.destroy()

        dialog.connect('response', dialog_response_cb)
        dialog.show()


# Signal handlers.


    def on_cancelbutton_clicked(self, widget, *args):
        wm.close(self)


    def on_okbutton_clicked(self, widget, *args):
        model = self.gamelist.get_model()
        iter = self.gamelist.get_active_iter()
        gamename = model.get_value(iter, 0)

        tableid = self.tablename.get_text()
        gameclass = SUPPORTED_GAMES[gamename]
        d = client.joinTable(tableid, gameclass, host=True)
        d.addCallbacks(self.createSuccess, self.createFailure)


    def on_tablename_changed(self, widget, *args):
        # Disable the OK button if the table name field is empty.
        sensitive = self.tablename.get_text() != ""
        self.newtable_okbutton.set_property('sensitive', sensitive)


    def on_window_delete_event(self, widget, *args):
        wm.close(self)

