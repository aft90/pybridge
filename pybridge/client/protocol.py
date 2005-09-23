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


import sha, shlex
from twisted.protocols.basic import LineOnlyReceiver

from lib.core.enumeration import Seat


ACKNOWLEDGEMENT, DENIED, ILLEGAL = 'ok', 'no', 'bad'
PROTOCOL = 'pybridge-0.1'


class PybridgeClientProtocol(LineOnlyReceiver):


	# Mapping between status events and corresponding listener functions.
	_status = {

		# Server events.
		'table_opened'   : 'tableOpened',
		'table_closed'   : 'tableClosed',
		'user_loggedin'  : 'userLoggedIn',
		'user_loggedout' : 'userLoggedOut',

		# Table events.
		'observer_joins'  : 'observerJoins',
		'observer_leaves' : 'observerLeaves',
		'player_joins'    : 'playerJoins',
		'player_leaves'   : 'playerLeaves',

		# Game events.
		'call_made'   : 'gameCallMade',
		'card_played' : 'gameCardPlayed',
		'contract'    : 'gameContract',
		'result'      : 'gameResult',

	}


	def __init__(self):
		self.listener = None
		self.pending  = {}  # Requests pending a response.
		self.tagIndex = 0


	def connectionMade(self):

		def response(signal, message):
			if signal == ACKNOWLEDGEMENT:
				self.listener.protocolGood(PROTOCOL)
			else:
				self.listener.protocolBad(PROTOCOL)

		self.sendCommand("protocol", (PROTOCOL,), response)


	def generateTag(self):
		"""Returns a free tag identifier and increments tag index."""
		tag = self.tagIndex
		self.tagIndex = (self.tagIndex + 1) % 10000
		return "#%s" % tag


	def lineReceived(self, line):
		print line

		tokens = shlex.split(line)
		tag = tokens[0]

		if tag[0] == '*':  # Status message.
			event, data = tokens[1], str.join(' ', tokens[2:])
			if event in self._status:
				# Call appropriate listener function.	
				dispatcher = getattr(self.listener, self._status[event])
				dispatcher(data)

		elif tag[0] == '#':
			handler = self.pending.get(tag, None)
			if handler:
				signal = tokens[1]
				if signal in (ACKNOWLEDGEMENT, DENIED, ILLEGAL):
					message = str.join(' ', tokens[2:])
					handler(signal, message)
				else:  # Data block.
					data = [str.split(str.strip(token, ","), ":") for token in tokens[2:]]
					handler(signal, data)
				del self.pending[tag]  # Free tag.


	def sendCommand(self, command, args=(), handler=None):
		"""Sends command and supplied arguments, to server."""
		tag = self.generateTag()
		line = str.join(" ", [str(token) for token in (tag, command) + args])
		if handler:
			self.pending[tag] = handler
		self.sendLine(line)


	def setListener(self, listener):
		self.listener = listener


	# Command handlers.


	def cmdGameCall(self, callType, bidLevel=None, bidDenom=None):
		self.sendCommand('call', (callType, bidLevel, bidDenom))


	def cmdGameHand(self, seat=None):

		def response(signal, data):
			print data

		self.sendCommand('hand', (seat,), response)


	def cmdGamePlay(self, rank, suit):
		self.sendCommand('play', (rank, suit))


	def cmdListTables(self):

		def response(signal, data):
			tables = []
			for datum in data:
				table = {}
				table['title'] = datum[0]
				table[Seat.North] = datum[1] or None
				table[Seat.East] = datum[2] or None
				table[Seat.South] = datum[3] or None
				table[Seat.West] = datum[4] or None
				tables.append(table)
			self.listener.tableListing(tables)
	
		self.sendCommand('list', ('tables',), response)


	def cmdListUsers(self):

		def response(signal, data):
			users = data
			self.listener.userListing(users)
	
		self.sendCommand('list', ('users',), response)


	def cmdLogin(self, username, password):

		def response(signal, message):
			if signal == ACKNOWLEDGEMENT:
				self.listener.loginGood()
			else:
				self.listener.loginBad()

		hash = sha.new(password)  # Use password hash.
		self.sendCommand('login', (username, hash.hexdigest()), response)


	def cmdLogout(self):
		self.sendCommand('logout')


	def cmdRegister(self, username, password):
		hash = sha.new(password)  # Use password hash.
		self.sendCommand('register', (username, hash.hexdigest()), None)


	def cmdTableCreate(self, identifier):

		def response(signal, message):
			if signal == ACKNOWLEDGEMENT:
				self.listener.tableCreated(identifier)
			else:
				print "bleep"

		self.sendCommand('create', (identifier,))


	def cmdTableLeave(self):
		self.sendCommand('leave')


	def cmdTableObserve(self, identifier):
		self.sendCommand('observe', (identifier,))


	def cmdTableSit(self, identifier, seat):
		self.sendCommand('sit', (identifier, seat))


	def cmdTableStand(self):
		self.sendCommand('stand')
