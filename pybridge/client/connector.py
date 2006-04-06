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

from events import ClientEvents, TableEvents


class Connector:
	""""""


	def __init__(self):
		self.avatar = None
		self.factory = pb.PBClientFactory()
		self.tables = {}  # Remote table objects.


	def _connect(self, host, port, username, password):
		"""Connect to server."""
		
		def connected(avatar):
			self.avatar = avatar
#			return avatar
	
		reactor.connectTCP(host, port, self.factory)
		creds = credentials.UsernamePassword(username, password)
		d = self.factory.login(creds, ClientEvents())
		d.addCallback(connected)
		
		return d


	def _failure(self, failure):
		"""For debugging purposes."""
		print failure, failure.getErrorMessage()


	def login(self, host, port, username, password):
		""""""
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


	def getTableEventHandler(self):
		return TableEvents


	def callServer(self, requestName, **kwargs):  # request
		"""Issues request to server."""
		if self.avatar:
			defer = self.avatar.callRemote(requestName, **kwargs)
#			defer.addErrback(self._failure)
			return defer


	def callTable(self, requestName, **kwargs):
		"""Issues request to joined table."""
		if len(self.tables) > 0:
			table = self.tables.values()[0]
			defer = table.callRemote(requestName, **kwargs)
#			defer.addErrback(self._failure)
			return defer


connector = Connector()

