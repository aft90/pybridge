from twisted.python import components

from lib.core.deck import Deck
from lib.core.game import Game
from lib.core.enumeration import Seat

import registry
registry = registry.getHandle()


class TableError(Exception): pass


class Table:
	"""A table sits four players and has any number of listeners."""


	def __init__(self):
		self._dealer    = Seat.North  # for now
		self._deck      = Deck()
		self._game      = None
		self._listeners = {}  # Listener interfaces, keyed by user identity.
		self._players   = dict.fromkeys(Seat.Seats, None)


	def addListener(self, identity, listener):
		"""Adds listener object.

		Since listener is an interface, the listener object must be provided by caller.
		"""
		if identity in self._listeners.keys():
			raise TableError("already at table")
		else:
			self._listeners[identity] = listener


	def addPlayer(self, identity, seat):
		"""Adds a player if:

		- identity has been added to listener list.
		- player is not already playing at the table.
		- the specified seat is empty.
		"""
		if identity not in self._listeners.keys():
			raise TableError("not at table")
		elif self._players[seat]:
			raise TableError("seat occupied")
		else:
			self._players[seat] = identity
			[listener.tablePlayerJoin(identity) for listener in self._listeners]


	def gameMakeCall(self, identity, call):
		"""Make call."""
		if identity not in self._players.values():
			raise TableError("unavailable")
		elif self._game is None:
			raise TableError("unavailable")
		else:
			seat = [seat for seat, player in self._players.items() if player==identity][0]
			self._game.makeCall(seat, call)
			for listener in self._listeners:
				listener.gameCallMade(seat, call)


	def gamePlayCard(self, identity, card):
		"""Play card."""
		if identity not in self._players.values():
			raise TableError("unavailable")
		elif self._game is None:
			raise TableError("unavailable")
		else:
			seat = [seat for seat, player in self._players.items() if player==identity][0]
			self._game.playCard(seat, card)
			for listener in self._listeners:
				listener.gameCardPlayed(seat, card)


	def gameStart(self):
		"""Instantiates game object."""
		if self._game is not None:
			raise TableError("game in progress")
		elif len([seat for seat in self.players.values() if seat is None]) > 0:
			raise TableError("seat vacant")
		else:
			deal = self._deck.generateRandom()
			self._game = Game(self._dealer, deal, vulnNS=False, vulnEW=False)
			[listener.gameStarted() for listener in self._listeners]


	def removeListener(self, identity):
		"""Removes identity from listener list.""" 
		if identity in self._listeners.keys():
			self._listeners.remove(listener)
		else:
			raise TableError("not at table")


	def removePlayer(self, player):
		"""Removes player from seat."""
		if player in self._players.values():
			seat = [seat for seat, identifier in self._players.items() if identifier==player][0]
			self._players[seat] = None
			[listener.playerLeave(player) for listener in self._listeners]
		else:
			raise TableError("not at table")


class ITableListener(components.Interface):
	"""The ITableListener interface allows monitoring of a table."""

	def gameCallMade(self, player, call):
		"""Called when player makes a call in this game."""

	def gameCardPlayed(self, player, card):
		"""Called when player plays a card in this game."""

	def gameStarted(self):
		"""Called when game starts."""

	def gameResult(self, result):
		"""Called when game result is known."""

	def observerJoin(self, person):
		"""Called when an observer joins this table."""

	def observerLeave(self, person):
		"""Called when an observer leaves this table."""

	def playerJoin(self, person, seat):
		"""Called when a player joins this table."""

	def playerLeave(self, person):
		"""Called when a player leaves this table."""
