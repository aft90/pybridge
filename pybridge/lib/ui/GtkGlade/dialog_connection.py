# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2005 PyBridge Project.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA


import gtk
from wrapper import WidgetWrapper


class DialogConnection(WidgetWrapper):

	widget_name = 'dialog_connection'


	def new(self):
		pass


	def get_connection_parameters(self):
		"""Returns parameters for connection to server."""
		return {'host'     : self.hostname.get_active_text(),
		        'port'     : 5040,
		        'username' : self.username.get_text(),
		        'password' : self.password.get_text()}


	def connection_failure(self, message):
		print message
		self.okbutton.set_property('sensitive', True)


	# Signal handlers.


	def on_dialog_connection_destroy(self, widget, *args):
		self.ui.shutdown()


	def on_cancelbutton_clicked(self, widget, *args):
		self.ui.shutdown()


	def on_hostname_changed(self, widget, *args):
		sensitive = (self.hostname.get_active_text() and self.username.get_text()) != ""
		self.okbutton.set_property('sensitive', sensitive)


	def on_username_changed(self, widget, *args):
		self.on_hostname_changed(self, widget, *args)


	def on_okbutton_clicked(self, widget, *args):
		self.okbutton.set_property('sensitive', False)  # Prevent repeat clicks.
		self.ui.connect(self.get_connection_parameters())
