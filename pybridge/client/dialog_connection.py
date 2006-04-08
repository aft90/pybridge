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
from settings import settings
from windowmanager import windowmanager


class DialogConnection(GladeWrapper):

	glade_name = 'dialog_connection'


	def new(self):
		# Read connection parameters from client settings.
		self.entry_hostname.set_text(settings.get('connection', 'hostname'))
		self.entry_username.set_text(settings.get('connection', 'username'))
		password = settings.get('connection', 'password')
		if password:
			self.entry_password.set_text(password)
			self.check_savepassword.set_active(True)


	def connect_success(self, avatar):
		"""Actions to perform when connecting succeeds."""
		# Save hostname/username to settings.
		settings.set('connection', 'hostname', self.entry_hostname.get_text())
		settings.set('connection', 'username', self.entry_username.get_text())
		if self.check_savepassword.get_active():
			settings.set('connection', 'password', self.entry_password.get_text())
		else:	# Flush password.
			settings.set('connection', 'password', '')
		
		# Launch main window.
		windowmanager.terminate('dialog_connection')
		windowmanager.launch('window_main')


	def connect_failure(self, failure, error):
		"""Actions to perform when connecting fails."""
		print failure.getErrorMessage()
		error_dialog = gtk.MessageDialog(
			parent = self.window,
			flags = gtk.DIALOG_MODAL,
			type = gtk.MESSAGE_ERROR,
			buttons = gtk.BUTTONS_OK,
			message_format = error
		)
		error_dialog.run()
		error_dialog.destroy()
		self.button_connect.set_property('sensitive', True)


# Signal handlers.


	def on_dialog_connection_delete_event(self, widget, *args):
		windowmanager.shutdown()


	def on_hostname_changed(self, widget, *args):
		sensitive = self.entry_hostname.get_text() != "" and self.entry_username.get_text() != ""
		self.button_connect.set_property('sensitive', sensitive)


	def on_username_changed(self, widget, *args):
		self.on_hostname_changed(self, widget, *args)  # Same as host field.


	def on_connect_clicked(self, widget, *args):
		self.button_connect.set_property('sensitive', False)  # Prevent repeat clicks.
		
		hostname = self.entry_hostname.get_text()
		port = settings.getint('connection', 'portnum')
		username = self.entry_username.get_text()
		password = self.entry_password.get_text()
		
		if self.check_registeruser.get_active() == True:  # Register new user.
			d = connector.register(hostname, port, username, password)
			d.addCallback(lambda r: connector.login(hostname, port, username, password))
			d.addCallback(self.connect_success)
			d.addErrback(self.connect_failure, 'Registration failed.')
		else:  # Just log in.
			d = connector.login(hostname, port, username, password)
			d.addCallback(self.connect_success)
			d.addErrback(self.connect_failure, 'Login failed.')


	def on_quit_clicked(self, widget, *args):
		windowmanager.shutdown()

