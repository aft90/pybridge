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


import re, shlex

from twisted.internet import protocol, reactor
from twisted.protocols import basic

from lib.core.enumeration import CallType, Denomination, Rank, Suit

from table import ITableListener

import registry
registry = registry.getHandle()


SUPPORTED_PROTOCOLS = ('0.0.0', '0.0.1')


class Acknowledgement(Exception): pass
class DeniedCommand(Exception): pass
class IllegalCommand(Exception): pass


class ClientProtocol(basic.LineOnlyReceiver):


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
		'password'  : 'cmdPassword',
		'set'       : 'cmdVariableSet',
		'shout'     : 'cmdTalkShout',
		'silence'   : 'cmdSilence',
		'tell'      : 'cmdTalkTell',
		'unsilence' : 'cmdUnsilence',
		
		# Non-table commands.
		'host'    : 'cmdTableHost',
		'join'    : 'cmdTableJoin',
		'observe' : 'cmdTableObserve',

		# Table commands.
		'chat'   : 'cmdTalkChat',
		'kibitz' : 'cmdTalkKibitz',
		'leave'  : 'cmdTableLeave',

		# Table host commands.
		'invite' : 'cmdTableHostInvite',
		'kick'   : 'cmdTableHostKick',
		'start'  : 'cmdTableHostStartGame',

		# Game commands.
		'history'   : 'cmdGameHistory',
		'turn'      : 'cmdGameTurn',

		# Game player commands.
		'accept'   : 'cmdGameClaimAccept',
		'alert'    : 'cmdGameAlert',
		'call'     : 'cmdGameCall',
		'cards'    : 'cmdGameCards',
		'claim'    : 'cmdGameClaimClaim',
		'concede'  : 'cmdGameClaimConcede',
		'decline'  : 'cmdGameClaimDecline',
		'play'     : 'cmdGamePlay',
		'retract'  : 'cmdGameClaimRetract'

	}


	def __init__(self):
		self.session = dict.fromkeys(('protocol', 'username', 'table'), None)  # Required for state tracking.


	def connectionLost(self, reason):
		if self.session['username']:
			registry.userLogout(self.session['username'])


	def getIdentifier(self):
		return self.session['username']


	def lineReceived(self, line):
		tag, tokens = "-", shlex.split(line)
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
				dispatcher(*arguments)  # Execution.
			else:
				raise IllegalCommand("invalid number of arguments")
		
		except Acknowledgement:
			self.sendTokens(tag, "ok")
		except DeniedCommand, error:  # Command is irrelevant.
			self.sendTokens(tag, "no", error)
		except IllegalCommand, error:  # Command is ill-formatted.
			self.sendTokens(tag, "bad", error)


	def sendStatus(self, subject, action=None, object=None):
		"""Sends status message to client. Note SUBJECT performs ACTION on OBJECT."""
		self.sendTokens("*", subject, action, object)


	def sendTokens(self, *tokens):
		"""Sends string of tokens to client."""
		self.sendLine(str.join(" ", [str(token) for token in tokens]))


	# Command handlers.


	def cmdGameCall(self, callType, bidLevel=None, bidDenom=None):
		self._checkStates(required=['player', 'game'])
		if callType not in CallType.CallTypes:
			raise IllegalCommand("invalid calltype")
		elif callType is CallType.Bid:
			if bidLevel not in ["1234567"]:
				raise IllegalCommand("invalid bid level")
			elif bidDenom not in Denomination.Denominations:
				raise IllegalCommand("invalid bid denomination")
			call = Call(CallType.Bid, int(bidLevel), bidDenom)
		else:
			call = Call(callType)  # Double or pass.
		try:
			self.session['table'].gameMakeCall(self.session['username'], call)
		except Table.GameError, error:
			raise IllegalCommand(error)


	def cmdGamePlay(self, rank, suit):
		self._checkStates(required=['player', 'game'])
		if rank not in Rank.Ranks:
			raise IllegalCommand("invalid rank")
		elif suit not in Suit.Suits:
			raise IllegalCommand("invalid suit")
		try:
			card = Card(rank, suit)
			self.session['table'].gamePlayCard(self.session['username'], card)
		except Table.GameError, error:
			raise IllegalCommand(error)


	def cmdLogin(self, username, password):
		self._checkStates(required=['loggedout'])  # Must not be logged in.
		if registry.userAuth(username, password):
			registry.userLogin(username, password, self)
			self.session['username'] = username
			raise Acknowledgement
		else:
			raise DeniedCommand("unrecognised username or bad password")


	def cmdLogout(self):
		self._checkStates(required=['loggedin'])  # Must be logged in.
		self._checkStates(forbidden=['game'], error="game in progress")
		registry.userLogout(self.session['username'])
		self.session['username'], self.session['table'] = None, None
		raise Acknowledgement


	def cmdProtocol(self, version):
		self._checkStates(required=['unverified'])
		if version not in SUPPORTED_PROTOCOLS:
			raise DeniedCommand("unsupported protocol")
		else:
			self.session['protocol'] = version
			raise Acknowledgement


	def cmdQuit(self):
		self.loseConnection()


	def cmdRegister(self, username, password):
		self._checkStates(required=['loggedout'])  # Must not be logged in.
		if registry.userRegister(username, password):
			raise Acknowledgement
		else:
			raise DeniedCommand("username taken")


	def cmdTableHost(self, identifier):
		self._checkStates(required=['loggedin'], forbidden=['table'])
		table = registry.tableCreate(identifier)
		self.session['table'] = table


	def cmdTableHostStartGame(self):
		self._checkStates(required=['table'])  # and host
		try:
			self.session['table'].gameStart()
		except TableError, error:
			raise DeniedCommand(error)


	def cmdTableJoin(self, identifier, seat):
		self._checkStates(required=['loggedin'], forbidden=['table'])
		if seat not in Seat.Seats:
			raise InvalidCommand("invalid seat")
		table = registry.getTable(identifier)
		if table:
			try:
#				table.addObserver(self.session['username'])
				table.addPlayer(self.session['username'], seat)
				self.session['table'] = table
			except TableError, error:
				raise DeniedCommand(error)


	def cmdTableLeave(self):
		self._checkStates(required=['loggedin', 'table'])
		try:
			self.session['table'].removePlayer(self.session['username'])
			self.session['table'] = None
		except TableError, error:
			raise DeniedCommand(error)


	def cmdTableObserve(self, table):
		pass


	def cmdUserFinger(self, user):
		self._checkStates(required=['loggedin'])
		fields = registry.getFinger(identifier)
		if fields:
			[self.sendStatus(name, ":", value) for name, value in fields]
			raise Acknowledgement
		else:
			raise DeniedCommand("invalid user")


	def cmdVariableGet(self, name):
		self._checkStates(required=['loggedin'])
		value = registry.getVariable(self.session['username'], name)
		if value:
			self.sendStatus(name, ":", value)
		else:
			raise DeniedCommand("unknown variable")


	def cmdVariableSet(self, name, value):
		self._checkStates(required=['loggedin'])
		if registry.getVariable(self.session['username'], name):  # Valid variable.
			registry.setVariable(self.session['username'], name, value)
		else:
			raise DeniedCommand("unknown variable")


	def _checkStates(self, required=(), forbidden=(), error="unavailable"):
		"""Raises DeniedCommand(error) if:

		- one or more required states are not present.
		- one or more forbidden states are present.
		"""
		# TODO: once Python 2.4+ becomes standard, replace lists with sets.
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
			if self.session['username'] in self.session['table']._players.values():  # TODO: This is stupid. Fix.
				states.append('player')
			else:
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


class ProtocolTableListener:

	__implements__ = (ITableListener,)


	def __init__(self, client):
		self._client = client

	def gameCallMade(self, player, call):
		self._client.sendStatus(player, "calls", call)

	def gameCardPlayed(self, player, card):
		self._client.sendStatus(player, "plays", card)

	def gameStarted(self):
		pass

	def gameResult(self, result):
		self._client.sendStatus("result", result)

	def observerJoin(self, observer):
		self._client.sendStatus("observer", "joins", observer)

	def observerLeave(self, observer):
		self._client.sendStatus("observer", "leaves", observer)

	def playerJoin(self, player):
		self._client.sendStatus("player", "joins", player)

	def playerLeave(self, player):
		self._client.sendStatus("player", "leaves", player)
