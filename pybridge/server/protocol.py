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

	_commands = {

		# Connection and session control.
		"login"    : "cmdLogin",
		"logout"   : "cmdLogout",
		"protocol" : "cmdProtocol",
		"quit"     : "cmdQuit",

		# Server commands.
		"finger"    : "cmdFinger",
		"get"       : "cmdVariableGet",
		"password"  : "cmdPassword",
		"set"       : "cmdVariableSet",
		"shout"     : "cmdTalkShout",
		"silence"   : "cmdSilence",
		"tell"      : "cmdTalkTell",
		"unsilence" : "cmdUnsilence",
		
		# Non-table commands.
		"host"    : "cmdHost",
		"join"    : "cmdJoin",
		"observe" : "cmdObserve",

		# Table commands.
		"chat"   : "cmdTalkChat",
		"kibitz" : "cmdTalkKibitz",
		"leave"  : "cmdTableLeave",

		# Table host commands.
		"invite" : "cmdTableInvite",
		"kick"   : "cmdTableKick",

		# Game commands.
		"history"   : "cmdGameHistory",
		"whoseturn" : "cmdGameTurn",

		# Game player commands.
		"accept"   : "cmdGameClaimAccept",
		"alert"    : "cmdGameAlert",
		"call"     : "cmdGameCall",
		"cards"    : "cmdGameCards",
		"claim"    : "cmdGameClaimClaim",
		"concede"  : "cmdGameClaimConcede",
		"decline"  : "cmdGameClaimDecline",
		"play"     : "cmdGamePlay",
		"retract"  : "cmdGameClaimRetract"

	}


	def __init__(self):
		self._registered = False  # True if client instance in registry, False otherwise.
		self._username   = None
		self._version    = None   # Client protocol version.


	def connectionLost(self, reason):
		if self._registered:
			registry.removeClient(self)


	def getIdentifier(self):
		return self._username or None


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
			argsMax = dispatcher.func_code.co_argcount - 1  # "self" is an argument.
			argsMin = argsMax - len(dispatcher.func_defaults or [])

			if argsMin <= len(arguments) <= argsMax:
				dispatcher(*arguments)  # Execution
			else:
				raise IllegalCommand("invalid number of arguments")
		
		except Acknowledgement:
			self.sendTokens(tag, "ok")
		except DeniedCommand, error:
			self.sendTokens(tag, "no", error)
		except IllegalCommand, error:  # Command is ill-formatted
			self.sendTokens(tag, "bad", error)


	def sendTokens(self, *tokens):
		self.sendLine(str.join(" ", [str(token) for token in tokens]))


	# Command handlers.


	def cmdGameCall(self, callType, bidLevel=None, bidDenom=None):
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
			self._table.gameMakeCall(self.getIdentifier(), call)
		except Table.GameError, error:
			raise IllegalCommand(error)


	def cmdGamePlay(self, rank, suit):
		if rank not in Rank.Ranks:
			raise IllegalCommand("invalid rank")
		elif suit not in Suit.Suits:
			raise IllegalCommand("invalid suit")
		try:
			card = Card(rank, suit)
			self._table.gamePlayCard(self._username, card)
		except Table.GameError, error:
			raise IllegalCommand(error)


	def cmdLogin(self, username, password):
		if self.getIdentifier():  # Already logged in.
			raise DeniedCommand("unavailable")
		elif registry.userAuth(username, password):
			self._username = username
			registry.addUser(self)
			raise Acknowledgement
		else:
			raise DeniedCommand("unrecognised username or bad password")


	def cmdLogout(self):
		if self.getIdentifier():
			try:
				registry.removeClient(self.getIdentifier())
				self._username = None
				raise Acknowledgement
			except registry.GameError:
				raise DeniedCommand("game in progress")
		else:
			raise DeniedCommand("unavailable")


	def cmdUserFinger(self, identifier):
		pass  # TODO


	def cmdProtocol(self, version):
		if self._version:
			raise DeniedCommand, "unavailable"
		elif version not in SUPPORTED_PROTOCOLS:
			raise DeniedCommand("unsupported protocol")
		else:
			self._version = version
			raise Acknowledgement


	def cmdQuit(self):
		pass  # TODO: drop connection
		# drop connection.


	def cmdVariableGet(self, name):
		if name in self._variables.keys():
			value = self._variables[name]
			self.sendData(tag, name, value)
		else:
			raise DeniedCommand("unknown variable")


	def cmdVariableSet(self, name, value):
		pass  # TODO


class ProtocolTableListener:

	__implements__ = (ITableListener,)


	def __init__(self, client):
		self._client = client

	def gameCallMade(self, player, call):
		self._client.sendData("*", "call_made", player, call)

	def gameCardPlayed(self, player, card):
		self._client.sendData("*", "card_played", player, card)

	def gameStarted(self):
		pass

	def gameResult(self, result):
		self._client.sendData("*", "result", result)

	def observerJoin(self, observer):
		self._client.sendData("*", "observer_join", observer)

	def observerLeave(self, observer):
		self._client.sendData("*", "observer_leave", observer)

	def playerJoin(self, player):
		self._client.sendData("*", "player_join", player)

	def playerLeave(self, player):
		self._client.sendData("*", "player_leave", player)


