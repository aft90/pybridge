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


from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator

from protocol import PybridgeClientProtocol


class Connector:
	""""""

	connection = None

	callbackSuccess = None
	callbackFailure = None


	def connect(self, host, port):
		"""Attempt to connect to PyBridge server."""
		if self.connection is None:
			creator = ClientCreator(reactor, PybridgeClientProtocol)
			defer = creator.connectTCP(host, port)
			defer.addCallbacks(self._connectSuccess, self._connectFailure)


	def disconnect(self):
		"""Disconnect from PyBridge server."""
		if self.connection is not None:
			self.connection.cmdQuit()
			self.connection = None


	def setSuccess(self, callback):
		"""Set a method to be called when connecting succeeds."""
		self.callbackSuccess = callback


	def setFailure(self, callback):
		"""Sets a method to be called when connecting fails."""
		self.callbackFailure = callback


	def _connectSuccess(self, connection):
		self.connection = connection
		
		def protocolResult(signal, reply):
			from pybridge.strings import CommandReply
			if signal == CommandReply.ACKNOWLEDGE:
				self.callbackSuccess()
			else:
				self.callbackFailure()
		
		# Verify protocol version transparently.
		self.connection.cmdProtocol(protocolResult)


	def _connectFailure(self, reason):
		error = reason.getErrorMessage()
		self.callbackFailure(error)


connector = Connector()

