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

from connector import connector
from windowmanager import windowmanager


class DialogNewtable(GladeWrapper):

	glade_name = 'dialog_newtable'


	def new(self):
		pass


# Signal handlers.


	def on_cancelbutton_clicked(self, widget, *args):
		windowmanager.terminate('dialog_newtable')


	def on_okbutton_clicked(self, widget, *args):
		
		def success(reference):
			# Add table reference to global tables dict.
			connector.tables[tablename] = reference
			windowmanager.terminate('dialog_newtable')
			windowmanager.get('window_main').join_table(tablename)

		def failure(reason):
			error = reason.getErrorMessage()
			error_dialog = gtk.MessageDialog(
				parent = self.window,
				flags = gtk.DIALOG_MODAL,
				type = gtk.MESSAGE_ERROR,
				buttons = gtk.BUTTONS_OK,
				message_format = error
			)
			error_dialog.run()
			error_dialog.destroy()
		
		from events import TableEvents
		tablename = self.entry_tablename.get_text()
		events = connector.getTableEventHandler()(tablename)
		defer = connector.callServer('hostTable', tablename=tablename,
		                             listener=events)
		defer.addCallbacks(success, failure)


	def on_tablename_changed(self, widget, *args):
		sensitive = self.entry_tablename.get_text() != ""
		self.okbutton.set_property('sensitive', sensitive)

