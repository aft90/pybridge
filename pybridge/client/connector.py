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


from twisted.cred import credentials
from twisted.internet import reactor
from twisted.spread import pb

from table import ClientBridgeTable
from windowmanager import windowmanager


class Connector(pb.Referenceable):
	"""Provides the glue between the client code and the server."""


	def __init__(self):
		self.avatar = None
		self.factory = pb.PBClientFactory()
		self.name = None  # User name.
		self.table = None  # ClientBridgeTable object.


	def _connect(self, host, port, username, password):
		"""Connect to server."""
		
		def connected(avatar):
			self.avatar = avatar
			self.name = username
	
		reactor.connectTCP(host, port, self.factory)
		creds = credentials.UsernamePassword(username, password)
		d = self.factory.login(creds, self)
		d.addCallback(connected)
		
		return d


	def login(self, host, port, username, password):
		"""Attempt to log in to server with username and password."""
		d = self._connect(host, port, username, password)
		return d


	def register(self, host, port, username, password):
		"""Registers username/password on server."""
		
		def try_register(avatar):
			d = self.avatar.callRemote('register', username, password)
			return d
		
		d = self._connect(host, port, '', '')  # Anonymous login.
		d.addCallback(try_register)
		return d


# Client request methods.


	def joinTable(self, tablename, host=False):
		
		def success(remote):
			table.remote = remote  # Set pointer to server-side object.
			self.table = table
			table.setup()
		
		table = ClientBridgeTable()
		request = (host and 'hostTable') or 'joinTable'
		d = self.avatar.callRemote(request, tablename=tablename, listener=table)
		d.addCallback(success)
		return d


	def leaveTable(self, tablename):
		d = self.avatar.callRemote('leaveTable', tablename=tablename)
		d.addCallback(lambda r: self.tables.pop(tablename))
		return d


	def listTables(self):
		return self.avatar.callRemote('listTables')


	def getTableInfo(self, tablename):
		return self.avatar.callRemote('getTableInfo', tablename=tablename)


# Event methods.


	def remote_messageReceived(self, type, sender, message):
		print "message " + message


	def remote_tableOpened(self, tablename):
		windowmanager.get('window_tablelisting').add_tables((tablename,))


	def remote_tableClosed(self, tablename):
		windowmanager.get('window_tablelisting').remove_tables((tablename,))


	def remote_userLoggedIn(self, username):
		print username + " connected"


	def remote_userLoggedOut(self, username):
		print username + " disconnected"


connector = Connector()

