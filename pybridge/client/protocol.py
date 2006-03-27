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


import sha, shlex
from twisted.protocols.basic import LineOnlyReceiver

from pybridge.conf import PYBRIDGE_PROTOCOL
from pybridge.common.enumeration import Seat
from pybridge.strings import CommandReply

from protocolcommands import ProtocolCommands
from protocolevents import ProtocolEvents


class PybridgeClientProtocol(LineOnlyReceiver, ProtocolCommands, ProtocolEvents):


	def __init__(self):
		self.pending  = {}	# Requests pending a response.
		self.tagIndex = 0


	def connectionMade(self):
		pass


	def connectionLost(self, reason):
		pass


	def generateTag(self):
		"""Returns a free tag identifier and increments tag index."""
		tag = "#%s" % self.tagIndex
		self.tagIndex = (self.tagIndex + 1) % 10000
		return tag


	def lineReceived(self, line):
		print line	# DEBUG DEBUG DEBUG

		tokens = shlex.split(line)
		tag, signal, data = tokens[0], tokens[1], tokens[2:]

		if tag[0] == '*':	# Status message.
			dispatcher = getattr(self, signal, None)
			if dispatcher:
				dispatcher(*data)	# Call event handler.

		elif tag[0] == '#':  # Reply to tagged command.
			handler = self.pending.get(tag, None)
			if handler:
				if signal == CommandReply.RESPONSE:
					handler(signal, data)
				else:
					handler(signal, str.join(' ', data))
				del self.pending[tag]	# Free tag.


	def sendCommand(self, command, handler, *args):
		"""Sends command and supplied arguments, to server."""
		tag = self.generateTag()
		params = ['\'%s\'' % arg for arg in args]
		line = str.join(" ", [str(token) for token in [tag, command] + params])
		if handler:
			self.pending[tag] = handler
		print line	# DEBUG DEBUG DEBUG
		self.sendLine(line)
