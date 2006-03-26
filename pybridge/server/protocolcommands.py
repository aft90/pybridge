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


from pybridge.common.bidding import Call
from pybridge.common.deck import Card
from pybridge.common.enumeration import CallType, Denomination, Level, Rank, Seat, Suit

from pybridge.strings import Command, Error

from table import TableError


# States that a client may be in.
UNVERIFIED, LOGGEDOUT, LOGGEDIN, TABLE, PLAYER, INGAME = range(6)


class ProtocolCommands:


# Connection and session control.


	def cmdLogin(self, username, password):
		self._checkStates(required=(LOGGEDOUT,))
		result = self.factory.userLogin(username, password, self)
		if result:  # Login failure.
			raise self.DeniedCommand(result)
		else:
			self.username = username


	def cmdLogout(self):
		self._checkStates(required=(LOGGEDIN,))
		self.factory.userLogout(self.username)
		self.username = None
		self.table = None


	def cmdProtocol(self, version):
		self._checkStates(required=(UNVERIFIED,))
		if version in self.SUPPORTED_PROTOCOLS:
			self.version = version
		else:
			raise self.DeniedCommand(Error.PROTOCOL_UNSUPPORTED)


	def cmdQuit(self):
		self.transport.loseConnection()  # Triggers connectionLost().


	def cmdRegister(self, username, password):
		self._checkStates(required=(LOGGEDOUT,))
		result = self.factory.userRegister(username, password)
		if result:  # Registration failure.
			raise self.DeniedCommand(result)


	def cmdVersion(self):
		raise self.Response("PyBridge Server")


# Server commands.


	def cmdList(self, request):
		self._checkStates(required=(LOGGEDIN,))
		if request == 'players':
			self._checkStates(required=(TABLE,))
			players = self.table.players.values()
			raise self.Response(*players)
		if request == 'tables':
			tables = self.factory.tables.keys()
			raise self.Response(*tables)
		elif request == 'users':
			users = self.factory.users.keys()
			raise self.Response(*users)
		elif request == 'observers':
			observers = self.table.observers.keys()
			raise self.Response(*observers)
		else:
			raise self.IllegalCommand("unknown request")


	def cmdHost(self, tablename):
		self._checkStates(required=(LOGGEDIN,), forbidden=(TABLE,))
		result = self.factory.tableOpen(tablename)
		if result:
			raise self.DeniedCommand(result)
		else:
			self.cmdObserve(tablename)  # Force.


	def cmdShout(self, message):
		self._checkStates(required=(LOGGEDIN,))
		recepients = self.factory.users.keys()
		self.factory.userTalk(self.username, recepients, message)


	def cmdTell(self, recepient, message):
		self._checkStates(required=(LOGGEDIN,))
		if recepient in self.factory.users.keys():
			self.factory.userTalk(self.username, (recepient,), message)
		else:
			raise self.DeniedCommand(Error.USER_UNKNOWN)


# Table commands.


	def cmdChat(self, message):
		self._checkStates(required=(TABLE,))
		recepients = self.table.observers.keys()
		self.factory.userTalk(self.username, recepients, message)


	def cmdKibitz(self, message):
		self._checkStates(required=(TABLE,), forbidden=(PLAYER,))
		recepients = [username for username in self.table.observers.keys() if username not in self.table.players.values()]
		self.factory.userTalk(self.username, recepients, message)


 	def cmdLeave(self):
		self._checkStates(required=(LOGGEDIN, TABLE))
		self.factory.tableRemoveUser(self.username, self.table.name)
		self.table = None


	def cmdObserve(self, tablename):
		self._checkStates(required=(LOGGEDIN,), forbidden=(TABLE,))
		table = self.factory.tables.get(tablename)
		if table:
			self.factory.tableAddUser(self.username, tablename)
			self.table = table
		else:
			raise self.DeniedCommand(Error.TABLE_UNKNOWN)


	def cmdSit(self, seat):
		self._checkStates(required=(TABLE,), forbidden=(PLAYER,))
		if seat not in Seat.Seats:
			raise self.IllegalCommand(Error.COMMAND_PARAMSPEC)
		result = self.table.playerAdd(self.username, seat)
		if result:
			raise self.DeniedCommand(result)


	def cmdStand(self):
		self._checkStates(required=(PLAYER,))
		result = self.table.playerRemove(self.username)
		if result:
			raise self.DeniedCommand(result)


# Game commands.


	def cmdHistory(self):
		self._checkStates(required=(INGAME,))
		raise self.IllegalCommand(Error.COMMAND_UNIMPLEMENTED)


	def cmdTurn(self):
		self._checkStates(required=(INGAME,))
		turn = self.table.game.whoseTurn()
		raise self.Response(turn)


# Game player commands.


	def cmdCall(self, callType, bidLevel=None, bidDenom=None):
		self._checkStates(required=(PLAYER, INGAME))
		
		if callType == CallType.Bid:
			if not (int(bidLevel) in Level.Levels and bidDenom in Denomination.Denominations):
				raise self.IllegalCommand(Error.COMMAND_PARAMSPEC)
			call = Call(CallType.Bid, int(bidLevel), bidDenom)
		elif callType in CallType.CallTypes:
			call = Call(callType)  # Double, redouble or pass.
		else:
			raise self.IllegalCommand(Error.COMMAND_PARAMSPEC)

		try:
			self.table.gameMakeCall(self.username, call)
		except TableError, error:
			raise self.DeniedCommand(error)


	def cmdHand(self, seat=None):
		self._checkStates(required=(INGAME,))
		if seat is None:  # Assume a player requesting own hand.
			self._checkStates(required=(PLAYER,), error=Error.COMMAND_UNAVAILABLE)
			seat = self.table.getSeatForPlayer(self.username)
			viewer = None
		elif seat in Seat.Seats and PLAYER in self._getStates():
			viewer = self.table.getSeatForPlayer(self.username)
		elif seat in Seat.Seats:  # An observer can view all hands.
			viewer = None
		else:
			raise self.IllegalCommand(Error.COMMAND_PARAMSPEC)
		try:
			hand = self.table.gameGetHand(seat, viewer)
			cards = [str(card) for card in hand]
			raise self.Response(str.join(", ", cards))
		except TableError, error:
			raise self.DeniedCommand(error)


	def cmdPlay(self, rank, suit):
		self._checkStates(required=(PLAYER, INGAME))
		if rank not in Rank.Ranks or suit not in Suit.Suits:
			raise self.IllegalCommand(Error.COMMAND_PARAMSPEC)
		card = Card(rank, suit)
		try:
			self.table.gamePlayCard(self.username, card)
		except TableError, error:
			raise self.DeniedCommand(error)


# Utility functions.


	def _checkStates(self, required=(), forbidden=(), error=Error.COMMAND_UNAVAILABLE):
		"""Raises DeniedCommand(error) if:

		- one or more required states are not present.
		- one or more forbidden states are present.
		"""
		# TODO: when Python 2.4 becomes standard, replace lists with sets.
		states      = self._getStates()
		missing     = [item for item in required if item not in states]
		conflicting = [item for item in forbidden if item in states]
		if len(missing + conflicting) > 0:
			raise self.DeniedCommand(error)


	def _getStates(self):
		"""Returns a list of current states."""
		states = []
		if self.table:
			states.append(TABLE)
			if self.username in self.table.players.values():
				states.append(PLAYER)
			if self.table.game:  # Game in progress.
				states.append(INGAME)
		if self.username:
			states.append(LOGGEDIN)
		elif self.version:
			states.append(LOGGEDOUT)
		else:
			states.append(UNVERIFIED)
		return states
