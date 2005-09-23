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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from twisted.python import components


class IFactoryListener(components.Interface):
	"""The IFactoryListener interface allows monitoring of server events."""

	def messageReceived(self, username, message):
		"""Called when a message is received from user."""

	def shutdown(self):
		"""Called when server is in the process of shutting down."""

	def tableOpened(self, tablename):
		"""Called when a table is created."""

	def tableClosed(self, tablename):
		"""Called when a table is closed."""

	def userLoggedIn(self, username):
		"""Called when user logs in."""

	def userLoggedOut(self, username):
		"""Called when user logs out."""
