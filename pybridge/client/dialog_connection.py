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
from wrapper import WindowWrapper


class DialogConnection(WindowWrapper):

	window_name = 'dialog_connection'


	def new(self):
		self.hostname.set_text(self.ui.config.get('hostname', ""))
		self.username.set_text(self.ui.config.get('username', ""))

		# If password is saved, we assume that we wish to save in the future.
		password = self.ui.config.get('password', "")
		self.password.set_text(password)
		self.save_password.set_active(password != "")


	def get_connection_parameters(self):
		"""Returns parameters for connection to server."""
		return {
			'hostname' : self.hostname.get_text(),
			'port'     : 5040,
			'username' : self.username.get_text(),
			'password' : self.password.get_text(),
			'register' : self.register_user.get_active()
		}


	def connect_success(self):
		"""Actions to perform after connecting successfully."""

		# Save host details to settings.
		self.ui.config['hostname'] = self.hostname.get_text()
		self.ui.config['username'] = self.username.get_text()
		if self.save_password.get_active():
			self.ui.config['password'] = self.password.get_text()
		else:
			self.ui.config['password'] = ""


	def connect_failure(self, reason):
		"""Actions to perform after connecting fails."""
		error_dialog = gtk.MessageDialog(
			type=gtk.MESSAGE_ERROR,
			buttons=gtk.BUTTONS_OK,
			message_format=reason
		).show()
		self.okbutton.set_property('sensitive', True)


	# Signal handlers.


	def on_dialog_connection_destroy(self, widget, *args):
		self.ui.shutdown()


	def on_cancelbutton_clicked(self, widget, *args):
		self.ui.shutdown()


	def on_hostname_changed(self, widget, *args):
		sensitive = (self.hostname.get_text() and self.username.get_text()) != ""
		self.okbutton.set_property('sensitive', sensitive)


	def on_username_changed(self, widget, *args):
		self.on_hostname_changed(self, widget, *args)


	def on_okbutton_clicked(self, widget, *args):
		self.okbutton.set_property('sensitive', False)  # Prevent repeat clicks.
		self.ui.connect(self.get_connection_parameters())
