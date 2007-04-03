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

from manager import wm


class DialogNewtable(GladeWrapper):

    glade_name = 'dialog_newtable'


    def new(self):
        pass


    def createSuccess(self, table):
        wm.close(self)


    def createFailure(self, reason):
        error = reason.getErrorMessage()
        dialog = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL,
                                   type=gtk.MESSAGE_ERROR,
                                   buttons=gtk.BUTTONS_OK)
        dialog.set_markup(_('Could not create new table.'))
        dialog.format_secondary_text(_('Reason: %s') % error)

        dialog.run()
        dialog.destroy()


# Signal handlers.


    def on_cancelbutton_clicked(self, widget, *args):
        wm.close(self)


    def on_okbutton_clicked(self, widget, *args):
        tableid = self.entry_tablename.get_text()
        d = self.parent.joinTable(tableid, host=True)
        d.addCallbacks(self.createSuccess, self.createFailure)


    def on_tablename_changed(self, widget, *args):
        sensitive = self.entry_tablename.get_text() != ""
        self.okbutton.set_property('sensitive', sensitive)

