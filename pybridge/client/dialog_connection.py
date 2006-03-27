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

from pybridge.conf import TCP_PORT
from connector import connector
from settings import settings
from windowmanager import windowmanager


class DialogConnection(GladeWrapper):

	glade_name = 'dialog_connection'


	def new(self):
		# Read connection parameters from client settings.
		self.hostname.set_text(settings.get('Server', 'hostname'))
		self.username.set_text(settings.get('Server', 'username'))
		
		password = settings.get('Server', 'password')
		if password:
			self.password.set_text(password)
			self.save_password.set_active(True)

		# Set up connector success and failure callbacks.
		connector.setSuccess(self.connect_success)
		connector.setFailure(self.connect_failure)


	def connect_success(self):
		"""Actions to perform after connecting successfully."""
		username = self.username.get_text()
		password = self.password.get_text()

		if self.register_user.get_active():
			connector.connection.cmdRegister(username, password)

		# A callback.
		def loginResult(signal, reply):
			from pybridge.strings import CommandReply
			if signal == CommandReply.ACKNOWLEDGE:
				self.login_success()
			else:
				self.login_failure(reply)

		connector.connection.cmdLogin(username, password, loginResult)


	def connect_failure(self, error):
		"""Actions to perform after connecting fails."""
		error_dialog = gtk.MessageDialog(
			parent = self.window,
			flags = gtk.DIALOG_MODAL,
			type = gtk.MESSAGE_ERROR,
			buttons = gtk.BUTTONS_OK,
			message_format = error
		)
		error_dialog.run()
		error_dialog.destroy()
		self.connectbutton.set_property('sensitive', True)


	def login_success(self):
		"""Actions to perform when login succeeds."""
		
		# Save hostname/username to settings.
		settings.set('Server', 'hostname', self.hostname.get_text())
		settings.set('Server', 'username', self.username.get_text())
		if self.save_password.get_active():
			settings.set('Server', 'password', self.password.get_text())
		else:	# Flush password.
			settings.set('Server', 'password', '')
		
		# Launch main window.
		windowmanager.destroy('dialog_connection')
		windowmanager.launch('window_main')


	def login_failure(self, error):
		"""Actions to perform when login fails."""
		
		connector.disconnect()	# Drop connection.
		
		error_dialog = gtk.MessageDialog(
			parent = self.window,
			flags = gtk.DIALOG_MODAL,
			type = gtk.MESSAGE_ERROR,
			buttons = gtk.BUTTONS_OK,
			message_format = error
		)
		error_dialog.run()
		error_dialog.destroy()
		self.connectbutton.set_property('sensitive', True)


# Signal handlers.


	def on_dialog_connection_destroy(self, widget, *args):
		windowmanager.shutdown()


	def on_hostname_changed(self, widget, *args):
		sensitive = (self.hostname.get_text() and self.username.get_text()) != ""
		self.connectbutton.set_property('sensitive', sensitive)


	def on_username_changed(self, widget, *args):
		self.on_hostname_changed(self, widget, *args)	# Same as host field.


	def on_connectbutton_clicked(self, widget, *args):
		self.connectbutton.set_property('sensitive', False)	# Prevent repeat clicks.
		hostname = self.hostname.get_text()
		connector.connect(self.hostname.get_text(), TCP_PORT)	# Hostname and port.


	def on_quitbutton_clicked(self, widget, *args):
		windowmanager.shutdown()

