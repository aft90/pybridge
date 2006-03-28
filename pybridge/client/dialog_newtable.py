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
		tablename = self.tablename.get_text()
		connector.connection.cmdHost(tablename)
		windowmanager.terminate('dialog_newtable')


	def on_tablename_changed(self, widget, *args):
		sensitive = self.tablename.get_text() != ""
		self.okbutton.set_property('sensitive', sensitive)

