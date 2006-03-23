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


import shlex
from twisted.protocols.basic import LineOnlyReceiver

from pybridge.conf import PYBRIDGE_PROTOCOL, PYBRIDGE_VERSION
from pybridge.common.bidding import Call
from pybridge.common.deck import Card
from pybridge.common.enumeration import CallType, Denomination, Level, Rank, Seat, Suit
from pybridge.interface import COMMANDS, STATUS, IProtocolListener

# Command response types.
ACKNOWLEDGEMENT, DATA, DENIED, ILLEGAL = 'ok', 'data', 'no', 'bad'

# States that a client may be in.
UNVERIFIED, LOGGEDOUT, LOGGEDIN, TABLE, PLAYER, INGAME = range(6)

SUPPORTED_PROTOCOLS = (PYBRIDGE_PROTOCOL,)


class Acknowledgement(Exception): pass
class DeniedCommand(Exception): pass
class IllegalCommand(Exception): pass
class Response(Exception): pass


class PybridgeServerProtocol(LineOnlyReceiver):
	
	__implements__ = (IProtocolListener,)


	def __init__(self):
		self.username = None
		self.table = None
		self.version = None  # Version of client protocol.


	def connectionMade(self):
		self.sendStatus('version', 'PyBridge Server %s' % PYBRIDGE_VERSION)
		

	def connectionLost(self, reason):
		if self.username:
			self.factory.userLogout(self.username)


	def lineReceived(self, line):
		tokens = shlex.split(line)
		try:
			# Check for a command.
			if len(tokens) == 0:
				tag = '-'
				raise IllegalCommand("command required")
			elif len(tokens) == 1 and tokens[0][0] == '#':
				tag = tokens[0]
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
			if command not in COMMANDS:
				raise IllegalCommand("unknown command")
			
			# Argument verification.
			dispatcher = getattr(self, COMMANDS[command])
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
			self.sendReply(tag, DENIED, error)
		except IllegalCommand, error:  # Command is ill-formatted.
			self.sendReply(tag, ILLEGAL, error)
		except Response, tokens:
			self.sendReply(tag, DATA, *tokens.args)


	def sendReply(self, tag, signal, *args):
		"""Sends reply message to client."""
		tokens = ["\'%s\'" % str(arg).strip() for arg in args]
		self.sendLine(str.join(' ', [tag, signal] + tokens))


	def sendStatus(self, event, *args):
		"""Sends status message to client."""
		tokens = ["\'%s\'" % str(arg).strip() for arg in args]
		self.sendLine(str.join(' ', ['*', event] + tokens))


# Connection and session control.


	def cmdLogin(self, username, password):
		self._checkStates(required=(LOGGEDOUT,))
		result = self.factory.userLogin(username, password, self)
		if result:  # Login failure.
			raise DeniedCommand(result)
		else:
			self.username = username

	def cmdLogout(self):
		self._checkStates(required=(LOGGEDIN,))
		self.factory.userLogout(self.username)
		self.username, self.table = None, None


	def cmdProtocol(self, version):
		self._checkStates(required=(UNVERIFIED,))
		if version in SUPPORTED_PROTOCOLS:
			self.version = version
		else:
			raise DeniedCommand("unsupported protocol")


	def cmdQuit(self):
		self.transport.loseConnection()  # Triggers connectionLost().


	def cmdRegister(self, username, password):
		self._checkStates(required=(LOGGEDOUT,))
		result = self.factory.userRegister(username, password)
		if result:  # Registration failure.
			raise DeniedCommand(result)


# Server commands.


	def cmdList(self, request):
		self._checkStates(required=(LOGGEDIN,))
		if request == 'players':
			self._checkStates(required=(TABLE,))
			players = self.table.players.values()
			raise Response(*players)
		if request == 'tables':
			tables = self.factory.tables.keys()
			raise Response(*tables)
		elif request == 'users':
			users = self.factory.users.keys()
			raise Response(*users)
		elif request == 'observers':
			observers = self.table.observers.keys()
			raise Response(*observers)
		else:
			raise IllegalCommand("unknown request")


	def cmdPassword(self, oldPassword, newPassword):
		self._checkStates(required=(LOGGEDIN,))
		# TODO: something here.
		raise IllegalCommand("not implemented yet")


	def cmdTableHost(self, tablename):
		self._checkStates(required=(LOGGEDIN,), forbidden=(TABLE,))
		result = self.factory.tableOpen(tablename)
		if result:
			raise DeniedCommand(result)
		else:
			self.cmdTableObserve(tablename)


	def cmdTalkShout(self, message):
		self._checkStates(required=(LOGGEDIN,))
		recepients = self.factory.users.keys()
		self.factory.userTalk(self.username, recepients, message)


	def cmdTalkTell(self, recepient, message):
		self._checkStates(required=(LOGGEDIN,))
		if recepient in self.factory.users.keys():
			self.factory.userTalk(self.username, (recepient,), message)
		else:
			raise DeniedCommand("invalid username")


# Table commands.


	def cmdTalkChat(self, message):
		self._checkStates(required=(TABLE,))
		recepients = self.table.observers.keys()
		self.factory.userTalk(self.username, recepients, message)


	def cmdTalkKibitz(self, message):
		self._checkStates(required=(TABLE,), forbidden=(PLAYER,))
		recepients = [username for username in self.table.observers.keys() if username not in self.table.players.values()]
		self.factory.userTalk(self.username, recepients, message)


 	def cmdTableLeave(self):
		self._checkStates(required=(LOGGEDIN, TABLE))
		self.factory.tableRemoveUser(self.username, self.table.name)
		self.table = None


	def cmdTableObserve(self, tablename):
		self._checkStates(required=(LOGGEDIN,), forbidden=(TABLE,))
		table = self.factory.tables.get(tablename)
		if table:
			self.factory.tableAddUser(self.username, tablename)
			self.table = table
		else:
			raise DeniedCommand("unknown table")


	def cmdTableSit(self, seat):
		self._checkStates(required=(TABLE,), forbidden=(PLAYER,))
		if seat not in Seat.Seats:
			raise IllegalCommand("invalid seat")
		result = self.table.playerAdd(self.username, seat)
		if result:
			raise DeniedCommand(result)


	def cmdTableStand(self):
		self._checkStates(required=(PLAYER,))
		result = self.table.playerRemove(self.username)
		if result:
			raise DeniedCommand(result)


# Game commands.


	def cmdGameHistory(self):
		self._checkStates(required=(INGAME,))
		raise IllegalCommand("not implemented yet")


	def cmdGameTurn(self):
		self._checkStates(required=(INGAME,))
		turn = self.table.game.whoseTurn()
		raise Response(turn)


# Game player commands.


	def cmdGameCall(self, callType, bidLevel=None, bidDenom=None):
		self._checkStates(required=(PLAYER, INGAME))
		
		if callType is CallType.Bid:
			if bidLevel not in Level.Levels:
				raise IllegalCommand("invalid bid level")
			elif bidDenom not in Denomination.Denominations:
				raise IllegalCommand("invalid bid denomination")
			call = Call(CallType.Bid, int(bidLevel), bidDenom)
		elif callType in CallType.CallTypes:
			call = Call(callType)  # Double, redouble or pass.
		else:
			raise IllegalCommand("invalid calltype")

		result = self.table.gameMakeCall(self.username, call)
		if result:
			raise DeniedCommand(result)


	def cmdGameHand(self, seat=None):
		self._checkStates(required=(INGAME,))
		if seat is None:
			self._checkStates(required=(PLAYER,), error="invalid seat")
			seat, position = self.table.getSeat(self.username), None
		elif seat in Seat.Seats and PLAYER in self._getStates():
			position = self.table.getSeat(self.username)
		elif seat in Seat.Seats:
			position = None
		else:
			raise IllegalCommand("invalid seat")
		cards = [str(card) for card in self.table.gameHand(seat, position)]
		raise Response(str.join(", ", cards))


	def cmdGamePlay(self, rank, suit):
		self._checkStates(required=(PLAYER, INGAME))
		if rank not in Rank.Ranks:
			raise IllegalCommand("invalid rank")
		elif suit not in Suit.Suits:
			raise IllegalCommand("invalid suit")
		card = Card(rank, suit)
		result = self.table.gamePlayCard(self.username, card)
		if result:
			raise DeniedCommand(result)


# Status events.


	def messageReceived(self, sender, message):
		self.sendStatus("message", sender, message)

	def shutdown(self):
		self.sendStatus("server_shutdown")

	def tableOpened(self, tablename):
		self.sendStatus("table_opened", tablename)

	def tableClosed(self, tablename):
		self.sendStatus("table_closed", tablename)

	def userJoinsTable(self, username, tablename):
		self.sendStatus("user_joins_table", username, tablename)

	def userLeavesTable(self, username, tablename):
		self.sendStatus("user_leaves_table", username, tablename)

	def userLoggedIn(self, username):
		self.sendStatus("user_loggedin", username)

	def userLoggedOut(self, username):
		self.sendStatus("user_loggedout", username)

	def gameCallMade(self, seat, call):
		self.sendStatus("game_call_made", "%s by %s" % (call, seat))

	def gameCardPlayed(self, seat, card):
		self.sendStatus("game_card_played", "%s by %s" % (card, seat))

	def gameContract(self, contract):
		doubles = {0 : "", 1 : "doubled", 2 : "redoubled"}
		format = (contract['bidLevel'], contract['bidDenom'], doubles[contract['doubleLevel']], contract['declarer'])
		self.sendStatus("game_contract", "%s %s %s by %s" % format)  # FIX THIS

	def gameResult(self, result):
		self.sendStatus("game_result", result)

	def gameStarted(self):
		self.sendStatus("game_started")

	def playerJoins(self, player, seat):
		self.sendStatus("player_joins", player, seat)

	def playerLeaves(self, player):
		self.sendStatus("player_leaves", player)


# Utility functions.


	def _checkStates(self, required=(), forbidden=(), error="unavailable"):
		"""Raises DeniedCommand(error) if:

		- one or more required states are not present.
		- one or more forbidden states are present.
		"""
		# TODO: when Python 2.4 becomes standard, replace lists with sets.
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
