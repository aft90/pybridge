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


import shlex

from twisted.protocols.basic import LineOnlyReceiver

from pybridge.common.bidding import Call
from pybridge.common.deck import Card
from pybridge.common.enumeration import CallType, Denomination, Rank, Seat, Suit

from pybridge.common.listener import IProtocolListener
from table import TableError


ACKNOWLEDGEMENT, DATA, DENIED, ILLEGAL = 'ok', 'data', 'no', 'bad'
UNVERIFIED, LOGGEDOUT, LOGGEDIN, TABLE, PLAYER, INGAME = range(6)
SUPPORTED_PROTOCOLS = ('pybridge-0.1',)


class Acknowledgement(Exception): pass
class DeniedCommand(Exception): pass
class IllegalCommand(Exception): pass
class Response(Exception): pass


class PybridgeServerProtocol(LineOnlyReceiver):


	# Mapping between command names and their executor functions.
	_commands = {

		# Connection and session control.
		'login'    : 'cmdLogin',
		'logout'   : 'cmdLogout',
		'protocol' : 'cmdProtocol',
		'quit'     : 'cmdQuit',
		'register' : 'cmdRegister',

		# Server commands.
		'list'     : 'cmdList',
		'password' : 'cmdPassword',
		'shout'    : 'cmdTalkShout',
		'tell'     : 'cmdTalkTell',
		
		# Table commands.
		'chat'    : 'cmdTalkChat,',
		'create'  : 'cmdTableCreate',
		'kibitz'  : 'cmdTalkKibitz',
		'observe' : 'cmdTableObserve',
		'leave'   : 'cmdTableLeave',
		'sit'     : 'cmdTableSit',
		'stand'   : 'cmdTableStand',

		# Game commands.
		'history' : 'cmdGameHistory',
		'turn'    : 'cmdGameTurn',

		# Game player commands.
		'accept'  : 'cmdGameClaimAccept',
		'alert'   : 'cmdGameAlert',
		'call'    : 'cmdGameCall',
		'claim'   : 'cmdGameClaimClaim',
		'concede' : 'cmdGameClaimConcede',
		'decline' : 'cmdGameClaimDecline',
		'hand'    : 'cmdGameHand',
		'play'    : 'cmdGamePlay',
		'retract' : 'cmdGameClaimRetract',

	}


	def __init__(self):
		self.username = None
		self.table = None
		self.version = None  # Version of client protocol.


	def connectionLost(self, reason):
		self.factory.userLogout(self.username)


	def getFactoryListener(self):
		"""Builds factory listener object."""
		return ProtocolFactoryListener(self)


	def getTableListener(self):
		"""Builds table listener object."""
		return ProtocolTableListener(self)


	def lineReceived(self, line):
		tokens = shlex.split(line)
		try:

			# Check for a command.
			if len(tokens) == 0:
				tag = '-'
				raise IllegalCommand("command required")
			elif len(tokens) == 1 and tokens[0][0] == '#':
				tag = '-'
				raise IllegalCommand("command required")

			# Get tag, command and any supplied arguments.
			if tokens[0][0] == '#':
				tag       = tokens[0]  # Tag provided.
				command   = tokens[1].lower()
				arguments = tokens[2:]
			else:
				tag       = '-'  # Use default '-' tag.
				command   = tokens[0].lower()
				arguments = tokens[1:]

			# Command verification.
			if command not in self._commands:
				raise IllegalCommand("unknown command")

			# Argument verification.
			dispatcher = getattr(self, self._commands[command])
			argsMax = dispatcher.func_code.co_argcount - 1  # "self"
			argsMin = argsMax - len(dispatcher.func_defaults or [])
			if argsMin > len(arguments) or argsMax < len(arguments):
				raise IllegalCommand("invalid number of arguments")

			# Call command, and be ready to trap resultant exceptions.
			dispatcher(*arguments)  # Execution.
			raise Acknowledgement   # (If we get this far.)
		
		except Acknowledgement:
			self.sendReply(tag, ACKNOWLEDGEMENT)
		except DeniedCommand, error:  # Command is irrelevant.
			self.sendReply(tag, DENIED, str(error))
		except IllegalCommand, error:  # Command is ill-formatted.
			self.sendReply(tag, ILLEGAL, str(error))
		except Response, inst:
			self.sendReply(tag, DATA, *inst.args)


	def sendReply(self, tag, signal, *args):
		"""Sends reply (to command with tag) to client."""
		tokens = ["\'%s\'" % arg.strip() for arg in args]
		self.sendLine(str.join(' ', [tag, signal] + tokens))


	def sendStatus(self, event, *args):
		"""Sends status message to client."""
		tokens = ["\'%s\'" % arg.strip() for arg in args]
		self.sendLine(str.join(' ', [str(token) for token in ['*', event] + tokens]))


	# Command handlers.


	def cmdGameCall(self, callType, bidLevel=None, bidDenom=None):
		self._checkStates(required=[PLAYER, INGAME])
		
		if callType is CallType.Bid:
			if bidLevel not in ('1', '2', '3', '4', '5', '6', '7'):
				raise IllegalCommand("invalid bid level")
			elif bidDenom not in Denomination.Denominations:
				raise IllegalCommand("invalid bid denomination")
			call = Call(CallType.Bid, int(bidLevel), bidDenom)
		elif callType in CallType.CallTypes:
			call = Call(callType)  # Double, redouble or pass.
		else:
			raise IllegalCommand("invalid calltype")

		try:
			self.table.gameMakeCall(self.username, call)
		except TableError:
			raise DeniedCommand("illegal call")


	def cmdGameHand(self, seat=None):
		self._checkStates(required=[INGAME])
		if seat is None:
			self._checkStates(required=[PLAYER], error="invalid seat")
			seat, position = self.table.getSeat(self.username), None
		elif seat in Seat.Seats and PLAYER in self._getStates():
			position = self.table.getSeat(self.username)
		elif seat in Seat.Seats:
			position = None
		else:
			raise IllegalCommand("invalid seat")
		cards = [str(card) for card in self.table.gameHand(seat, position)]
		raise Response(str.join(", ", cards))


	def cmdGameHistory(self):
		self._checkStates(required=[INGAME])
		# TODO: something.


	def cmdGamePlay(self, rank, suit):
		self._checkStates(required=[PLAYER, INGAME])
		if rank not in Rank.Ranks:
			raise IllegalCommand("invalid rank")
		elif suit not in Suit.Suits:
			raise IllegalCommand("invalid suit")
		card = Card(rank, suit)
		try:
			self.table.gamePlayCard(self.username, card)
		except TableError:
			raise DeniedCommand("illegal card")


	def cmdGameTurn(self):
		self._checkStates(required=[INGAME])
		turn = self.table.game.whoseTurn()
		raise Response(turn)


	def cmdList(self, request):
		self._checkStates(required=[LOGGEDIN])
		if request == 'players':
			self._checkStates(required=[TABLE])
			players = self.table.players.values()
			raise Response(*players)
		if request == 'tables':
			tables = self.factory.getTablesList()
			raise Response(*tables)
		elif request == 'users':
			users = self.factory.getUsersList()
			raise Response(*users)
		elif request == 'watchers':
			watchers = self.table.listeners.keys()
			raise Response(*watchers)
		else:
			raise IllegalCommand("unknown request")


	def cmdLogin(self, username, password):
		self._checkStates(required=[LOGGEDOUT])
		if self.factory.userLogin(username, password, self.getFactoryListener()):
			self.username = username
		else:
			raise DeniedCommand("unrecognised username or bad password")


	def cmdLogout(self):
		self._checkStates(required=[LOGGEDIN])
		self.factory.userLogout(self.username)
		self.username, self.table = None, None


	def cmdProtocol(self, version):
		self._checkStates(required=[UNVERIFIED])
		if version not in SUPPORTED_PROTOCOLS:
			raise DeniedCommand("unsupported protocol")
		else:
			self.version = version


	def cmdQuit(self):
		self.transport.loseConnection()


	def cmdRegister(self, username, password):
		self._checkStates(required=[LOGGEDOUT])  # Must not be logged in.
		if self.factory.userRegister(username, password):
			pass
		else:
			raise DeniedCommand("invalid username")


	def cmdTableCreate(self, tablename):
		self._checkStates(required=[LOGGEDIN], forbidden=[TABLE])
		if self.factory.tableOpen(tablename):
			pass
		else:
			raise DeniedCommand("invalid tablename")


	def cmdTableLeave(self):
		print self._getStates()
		self._checkStates(required=[LOGGEDIN, TABLE])
		self.factory.tableRemoveListener(self.username, self.table.name)
		self.table = None


	def cmdTableObserve(self, tablename):
		self._checkStates(required=[LOGGEDIN], forbidden=[TABLE])
		table = self.factory.getTable(tablename)
		if table:
			listener = self.getTableListener()
			self.factory.tableAddListener(self.username, tablename, listener)
			self.table = table
		else:
			raise DeniedCommand("unknown table")


	def cmdTableSit(self, seat):
		self._checkStates(required=[TABLE], forbidden=[PLAYER])
		if seat not in Seat.Seats:
			raise IllegalCommand("invalid seat")

		try:
			self.table.playerAdd(self.username, seat)
		except TableError, error:
			raise DeniedCommand(error)


	def cmdTableStand(self):
		self._checkStates(required=[PLAYER])
		try:
			self.table.playerRemove(self.username)
		except TableError, error:
			raise DeniedCommand(error)


	def cmdTalkChat(self, message):
		self._checkStates(required=[TABLE])
		recepients = self.table.listeners.keys()
		self.factory.userTalk(self.username, recepients, message)


	def cmdTalkKibitz(self, message):
		self._checkStates(required=[TABLE], forbidden=[PLAYER])
		recepients = [username for username in self.table.listeners.keys() if username not in self.table.players.values()]
		self.factory.userTalk(self.username, recepients, message)


	def cmdTalkShout(self, message):
		self._checkStates(required=[LOGGEDIN])
		recepients = self.factory.getUsersList()
		self.factory.userTalk(self.username, recepients, message)


	def cmdTalkTell(self, recepient, message):
		self._checkStates(required=[LOGGEDIN])
		if recepient in self.factory.getUsersList():
			self.factory.userTalk(self.username, (recepient,), message)
		else:
			raise DeniedCommand("invalid username")


	def _checkStates(self, required=(), forbidden=(), error="unavailable"):
		"""Raises DeniedCommand(error) if:

		- one or more required states are not present.
		- one or more forbidden states are present.
		"""
		# TODO: once Python 2.4 becomes standard, replace lists with sets.
		states      = self._getStates()
		missing     = [item for item in required if item not in states]
		conflicting = [item for item in forbidden if item in states]
		if len(missing + conflicting) > 0:
			raise DeniedCommand(error)


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


class ProtocolFactoryListener:

	__implements__ = (IProtocolListener,)


	def __init__(self, client):
		self._client = client

	def messageReceived(self, username, message):
		self._client.sendStatus("message", username, message)

	def shutdown(self):
		self._client.sendStatus("server_shutdown")

	def tableOpened(self, tablename):
		self._client.sendStatus("table_opened", tablename)

	def tableClosed(self, tablename):
		self._client.sendStatus("table_closed", tablename)

	def userJoinsTable(self, username, tablename):
		self._client.sendStatus("user_joins_table", username, tablename)

	def userLeavesTable(self, username, tablename):
		self._client.sendStatus("user_leaves_table", username, tablename)

	def userLoggedIn(self, username):
		self._client.sendStatus("user_loggedin", username)

	def userLoggedOut(self, username):
		self._client.sendStatus("user_loggedout", username)


class ProtocolTableListener:

	__implements__ = (IProtocolListener,)


	def __init__(self, client):
		self._client = client

	def gameCallMade(self, seat, call):
		self._client.sendStatus("game_call_made", "%s by %s" % (call, seat))

	def gameCardPlayed(self, seat, card):
		self._client.sendStatus("game_card_played", "%s by %s" % (card, seat))

	def gameContract(self, contract):
		doubles = {0 : "", 1 : "doubled", 2 : "redoubled"}
		format = (contract['bidLevel'], contract['bidDenom'], doubles[contract['doubleLevel']], contract['declarer'])
		self._client.sendStatus("game_contract", "%s %s %s by %s" % format)  # FIX THIS

	def gameResult(self, result):
		self._client.sendStatus("game_result", result)

	def gameStarted(self):
		self._client.sendStatus("game_started")

	def playerJoins(self, player, seat):
		self._client.sendStatus("player_joins", player, seat)

	def playerLeaves(self, player):
		self._client.sendStatus("player_leaves", player)
