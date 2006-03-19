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


ACKNOWLEDGEMENT, DATA, DENIED, ILLEGAL = 'ok', 'data', 'no', 'bad'
PROTOCOL = 'pybridge-0.1'


class PybridgeClientProtocol(LineOnlyReceiver):


	# Mapping between status events and corresponding listener functions.
	_status = {

		# Server events.
		'table_opened'      : 'tableOpened',
		'table_closed'      : 'tableClosed',
		'user_joins_table'  : 'userJoinsTable',
		'user_leaves_table' : 'userLeavesTable',
		'user_loggedin'     : 'userLoggedIn',
		'user_loggedout'    : 'userLoggedOut',

		# Table events.
		'player_joins'  : 'playerJoins',
		'player_leaves' : 'playerLeaves',

		# Game events.
		'game_call_made'   : 'gameCallMade',
		'game_card_played' : 'gameCardPlayed',
		'game_contract'    : 'gameContract',
		'game_result'      : 'gameResult',
		'game_started'     : 'gameStarted',

	}


	def __init__(self):
		self.listener = None
		self.pending  = {}  # Requests pending a response.
		self.tagIndex = 0


	def connectionMade(self):
		self.cmdProtocol()  # Verify protocol first.


	def generateTag(self):
		"""Returns a free tag identifier and increments tag index."""
		tag = "#%s" % self.tagIndex
		self.tagIndex = (self.tagIndex + 1) % 10000
		return tag


	def lineReceived(self, line):
		print line  # DEBUG DEBUG DEBUG

		tokens = shlex.split(line)
		tag, signal, data = tokens[0], tokens[1], tokens[2:]

		if tag[0] == '*':  # Status message.
			if signal in self._status:
				# Execute appropriate listener function.	
				dispatcher = getattr(self.listener, self._status[signal])
				dispatcher(*data)

		elif tag[0] == '#':  # Reply to tagged command.
			handler = self.pending.get(tag, None)
			if handler:
				if signal == DATA:
					handler(signal, data)
				else:
					handler(signal, str.join(' ', data))
				del self.pending[tag]  # Free tag.


	def sendCommand(self, command, args=(), handler=None):
		"""Sends command and supplied arguments, to server."""
		tag = self.generateTag()
		line = str.join(" ", [str(token) for token in (tag, command) + args])
		if handler:
			self.pending[tag] = handler
		print line  # DEBUG DEBUG DEBUG
		self.sendLine(line)


	def setListener(self, listener):
		self.listener = listener


	# Command handlers.


	def cmdGameCall(self, callType, bidLevel=None, bidDenom=None):
		self.sendCommand('call', (callType, bidLevel, bidDenom))


	def cmdGameHand(self, seat=None):

		def response(signal, data):
			pass

		self.sendCommand('hand', (seat,), response)


	def cmdGamePlay(self, rank, suit):
		self.sendCommand('play', (rank, suit))


	def cmdListTables(self):

		def response(signal, data):
			tables = data
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
				self.listener.loginSuccess()
			else:
				self.listener.loginFailure()

		hash = sha.new(password)  # Use password hash.
		self.sendCommand('login', (username, hash.hexdigest()), response)


	def cmdLogout(self):
		self.sendCommand('logout')


	def cmdProtocol(self):

		def response(signal, message):
			if signal == ACKNOWLEDGEMENT:
				self.listener.protocolSuccess(PROTOCOL)
			else:
				self.listener.protocolFailure(PROTOCOL)

		self.sendCommand("protocol", (PROTOCOL,), response)


	def cmdRegister(self, username, password):
		hash = sha.new(password)  # Use password hash.
		self.sendCommand('register', (username, hash.hexdigest()))


	def cmdTableCreate(self, tablename):

		def response(signal, message):
			if signal == ACKNOWLEDGEMENT:
				self.listener.tableCreated(tablename)

		self.sendCommand('create', (tablename,))


	def cmdTableLeave(self):
		self.sendCommand('leave')


	def cmdTableObserve(self, tablename):
		self.sendCommand('observe', (tablename,))


	def cmdTableSit(self, tablename, seat):
		self.sendCommand('sit', (tablename, seat))  # ??


	def cmdTableStand(self, tablename):
		self.sendCommand('stand', (tablename,))
