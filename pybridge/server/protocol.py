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


import string

from twisted.protocols.basic import LineOnlyReceiver

from lib.core.bidding import Call
from lib.core.enumeration import CallType, Denomination, Rank, Seat, Suit
from lib.core.deck import Card

from factory_interface import IFactoryListener
from table_interface import ITableListener
from table import TableError  # TODO: eliminate this dependency.


ACKNOWLEDGEMENT, DATA, DENIED, ILLEGAL = 'ok', 'data', 'no', 'bad'
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
		'finger'    : 'cmdFinger',
		'get'       : 'cmdVariableGet',
		'list'      : 'cmdList',
		'password'  : 'cmdPassword',
		'set'       : 'cmdVariableSet',
		'shout'     : 'cmdTalkShout',
		'silence'   : 'cmdSilence',
		'tell'      : 'cmdTalkTell',
		'unsilence' : 'cmdUnsilence',
		
		# Non-table commands.
		'create'  : 'cmdTableCreate',
		'observe' : 'cmdTableObserve',
		'sit'     : 'cmdTableSit',
		'stand'   : 'cmdTableStand',

		# Table commands.
		'chat'   : 'cmdTalkChat',
		'kibitz' : 'cmdTalkKibitz',
		'leave'  : 'cmdTableLeave',

		# Game commands.
		'history'   : 'cmdGameHistory',
		'turn'      : 'cmdGameTurn',

		# Game player commands.
		'accept'   : 'cmdGameClaimAccept',
		'alert'    : 'cmdGameAlert',
		'call'     : 'cmdGameCall',
		'claim'    : 'cmdGameClaimClaim',
		'concede'  : 'cmdGameClaimConcede',
		'decline'  : 'cmdGameClaimDecline',
		'hand'     : 'cmdGameHand',
		'play'     : 'cmdGamePlay',
		'retract'  : 'cmdGameClaimRetract'

	}


	def __init__(self):
		self.session = dict.fromkeys(('protocol', 'username', 'table'), None)


	def connectionLost(self, reason):
		if self.session['username']:
			self.cmdLogout()


	def getIdentifier(self):
		return self.session['username']


	def getFactoryListener(self):
		"""Builds factory listener object."""
		return ProtocolFactoryListener(self)


	def getTableListener(self):
		"""Builds table listener object."""
		return ProtocolTableListener(self)


	def lineReceived(self, line):
		tag, tokens = "-", string.split(line)
		try:

			# Check for a command.
			if len(tokens) == 0:
				raise IllegalCommand("command required")
			elif len(tokens) == 1 and tokens[0][0] == "#":
				raise IllegalCommand("command required")

			# Get tag, command and any supplied arguments.
			if tokens[0][0] == "#":  # Tag provided.
				tag, command, arguments = tokens[0], tokens[1].lower(), tokens[2:]
			else:
				command, arguments = tokens[0].lower(), tokens[1:]

			# Command verification.
			if command not in self._commands:
				raise IllegalCommand("unknown command")

			# Argument verification.
			dispatcher = getattr(self, self._commands[command])
			argsMax = dispatcher.func_code.co_argcount - 1  # "self"
			argsMin = argsMax - len(dispatcher.func_defaults or [])

			if argsMin <= len(arguments) <= argsMax:
				try:
					dispatcher(*arguments)  # Execution.
					raise Acknowledgement   # If we get this far.
				except TableError, error:
					raise DeniedCommand(error)
			else:
				raise IllegalCommand("invalid number of arguments")
		
		except Acknowledgement:
			self.sendTokens(tag, ACKNOWLEDGEMENT)
		except DeniedCommand, error:  # Command is irrelevant.
			self.sendTokens(tag, DENIED, "'%s'" % error)
		except IllegalCommand, error:  # Command is ill-formatted.
			self.sendTokens(tag, ILLEGAL, "'%s'" % error)
		except Response, data:
			self.sendTokens(tag, DATA, data)


	def sendStatus(self, event, **kwargs):
		"""Sends status message to client."""
		# For now, ignore keys and just send values.
		data = string.join(kwargs.values(), ",")
		self.sendTokens("*", event, data)


	def sendTokens(self, *tokens):
		"""Sends string of tokens to client."""
		self.sendLine(str.join(" ", [str(token) for token in tokens]))


	# Command handlers.


	def cmdGameCall(self, callType, bidLevel=None, bidDenom=None):
		self._checkStates(required=['player', 'game'])
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
		self.session['table'].gameMakeCall(self.session['username'], call)


	def cmdGameHand(self, seat=None):
		self._checkStates(required=['game'])
		if seat is None:
			self._checkStates(required=['player'], error="invalid seat")
			seat, position = self.session['table'].getSeat(self.session['username']), None
		elif seat in Seat.Seats and 'player' in self._getStates():
			position = self.session['table'].getSeat(self.session['username'])
		elif seat in Seat.Seats:
			position = None
		else:
			raise IllegalCommand("invalid seat")
		cards = [str(card) for card in self.session['table'].gameHand(seat, position)]
		raise Response(str.join(", ", cards))


	def cmdGameHistory(self):
		self._checkStates(required=['game'])
		# TODO: something.


	def cmdGamePlay(self, rank, suit):
		self._checkStates(required=['player', 'game'])
		if rank not in Rank.Ranks:
			raise IllegalCommand("invalid rank")
		elif suit not in Suit.Suits:
			raise IllegalCommand("invalid suit")
		card = Card(rank, suit)
		self.session['table'].gamePlayCard(self.session['username'], card)


	def cmdGameTurn(self):
		self._checkStates(required=['game'])
		turn = self.session['table']._game.whoseTurn()
		raise Response(turn)


	def cmdList(self, request):
		self._checkStates(required=['loggedin'])
		if request == 'tables':
			tables = self.factory.getTableList()
			raise Response(str.join(",", tables))
		elif request == 'users':
			users = self.factory.getUserList()
			raise Response(str.join(",", users))
		else:
			raise IllegalCommand("unknown request")


	def cmdLogin(self, username, password):
		self._checkStates(required=['loggedout'])
		if self.factory.userAuth(username, password):
			self.factory.userLogin(username, password, self.getFactoryListener())
			self.session['username'] = username
		else:
			raise DeniedCommand("unrecognised username or bad password")


	def cmdLogout(self):
		self._checkStates(required=['loggedin'])
		if self.session['table']:  # Leave table.
			self.session['table'].removeObserver(self.session['username'])
		self.factory.userLogout(self.session['username'])
		self.session['username'], self.session['table'] = None, None


	def cmdProtocol(self, version):
		self._checkStates(required=['unverified'])
		if version not in SUPPORTED_PROTOCOLS:
			raise DeniedCommand("unsupported protocol")
		else:
			self.session['protocol'] = version


	def cmdQuit(self):
		self.transport.loseConnection()


	def cmdRegister(self, username, password):
		self._checkStates(required=['loggedout'])  # Must not be logged in.
		if self.factory.userRegister(username, password):
			pass
		else:
			raise DeniedCommand("invalid username")


	def cmdTableCreate(self, tablename):
		self._checkStates(required=['loggedin'], forbidden=['table'])
		table = self.factory.tableOpen(tablename)


	def cmdTableLeave(self):
		self._checkStates(required=['loggedin', 'table'])
		self.session['table'].removeObserver(self.session['username'])
		self.session['table'] = None


	def cmdTableObserve(self, tablename):
		self._checkStates(required=['loggedin'], forbidden=['table'])
		table = self.factory.getTable(tablename)
		if table:
			table.addObserver(self.session['username'], self.getTableListener())
			self.session['table'] = table
		else:
			raise DeniedCommand("unknown table")


	def cmdTableSit(self, identifier, seat):
		self._checkStates(required=['loggedin'], forbidden=['player'])
		if seat not in Seat.Seats:
			raise IllegalCommand("invalid seat")
		table = self.factory.getTable(identifier)
		if not table:
			raise DeniedCommand("unknown table")
		if self.session['table']:
			# Already watching table. Must not be playing.
			if table is not self.session['table']:
				raise DeniedCommand("already at table")
			if self.session['table'].isPlayer(self.session['username']):
				raise DeniedCommand("already playing")  # TODO: shouldn't get here.
		else:
			# Not watching table, so add listener.
			table.addObserver(self.session['username'], self.getTableListener())
		try:
			table.addPlayer(self.session['username'], seat)
			self.session['table'] = table
		except TableError, error:
			raise DeniedCommand(error)


	def cmdTableStand(self):
		self._checkStates(required=['loggedin', 'player'])
		self.session['table'].removePlayer(self.session['username'])


#	def cmdUserFinger(self, username):
#		self._checkStates(required=['loggedin'])
#		fields = self.factory.getFinger(username)
#		if fields:
#			# TODO: no, no, no!
#			[self.sendStatus(name, value) for name, value in fields]
#		else:
#			raise DeniedCommand("invalid user")


#	def cmdVariableGet(self, name):
#		self._checkStates(required=['loggedin'])
#		value = self.factory.getVariable(self.session['username'], name)
#		if value:
#			self.sendStatus(name, value)
#		else:
#			raise DeniedCommand("unknown variable")


#	def cmdVariableSet(self, name, value):
#		self._checkStates(required=['loggedin'])
#		if self.factory.getVariable(self.session['username'], name):  # Valid variable.
#			self.factory.setVariable(self.session['username'], name, value)
#		else:
#			raise DeniedCommand("unknown variable")


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
		if self.session['table']:
			states.append('table')
			if self.session['table'].isPlayer(self.session['username']):
				states.append('player')
			if self.session['table'].isObserver(self.session['username']):
				states.append('observer')
			if self.session['table'].inProgress():
				states.append('game')
		if self.session['username']:
			states.append('loggedin')
		elif self.session['protocol']:
			states.append('loggedout')
		else:
			states.append('unverified')
		return states


class ProtocolFactoryListener:

	__implements__ = (IFactoryListener,)


	def __init__(self, client):
		self._client = client

	def messageReceived(self, username, message):
		self._client.sendStatus("message", user=username, message=message)

	def shutdown(self):
		self._client.sendStatus("server_shutdown")

	def tableOpened(self, tablename):
		self._client.sendStatus("table_opened", table=tablename)

	def tableClosed(self, tablename):
		self._client.sendStatus("table_closed", table=tablename)

	def userLoggedIn(self, username):
		self._client.sendStatus("user_loggedin", user=username)

	def userLoggedOut(self, username):
		self._client.sendStatus("user_loggedout", user=username)


class ProtocolTableListener:

	__implements__ = (ITableListener,)


	def __init__(self, client):
		self._client = client

	def gameCallMade(self, seat, call):
		self._client.sendStatus("call_made", "%s by %s" % (call, seat))

	def gameCardPlayed(self, seat, card):
		self._client.sendStatus("card_played", "%s by %s" % (card, seat))

	def gameContract(self, contract):
		doubles = {0 : "", 1 : "doubled", 2 : "redoubled"}
		format = (contract['bidLevel'], contract['bidDenom'], doubles[contract['doubleLevel']], contract['declarer'])
		self._client.sendStatus("contract", "%s %s %s by %s" % format)  # FIX THIS

	def gameResult(self, result):
		self._client.sendStatus("result", result=result)

	def observerJoins(self, observer):
		self._client.sendStatus("observer_joins", user=observer)

	def observerLeaves(self, observer):
		self._client.sendStatus("observer_leaves", user=observer)

	def playerJoins(self, player):
		self._client.sendStatus("player_joins", user=player)

	def playerLeaves(self, player):
		self._client.sendStatus("player_leaves", user=player)
