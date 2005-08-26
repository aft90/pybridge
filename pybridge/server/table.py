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


from twisted.python import components

from lib.core.deck import Deck
from lib.core.game import Game
from lib.core.enumeration import Seat


class TableError(Exception): pass


class Table:
	"""A table sits four players and has any number of listeners."""


	def __init__(self, identifier):
		self._dealer    = Seat.North  # for now
		self._deck      = Deck()
		self._game      = None
		self._identity  = identifier
		self._listeners = {}  # Listener interfaces, keyed by user identifier.
		self._players   = dict.fromkeys(Seat.Seats, None)


	def inProgress(self):
		"""Returns True if game in progress."""
		return self._game is not None


	def addListener(self, observer):
		"""Adds listener object as table observer."""
		identity = observer.getIdentifier()
		if identity in self._listeners:
			raise TableError("already at table")
		else:
			self._listeners[identity] = observer
			[listener.observerJoin(identity) for listener in self._listeners.values()]
			

	def addPlayer(self, player, seat):
		"""Adds a player if:

		- player object appears in _listeners.
		- player is not already playing at the table.
		- the specified seat is empty.
		"""
		if player not in self._listeners:
			raise TableError("not at table")
		elif player in self._players.values():
			raise TableError("already seated")
		elif self._players[seat]:
			raise TableError("seat occupied")
		else:
			self._players[seat] = player
			[listener.tablePlayerJoin(player) for listener in self._listeners.values()]


	def gameMakeCall(self, player, call):
		"""Make call."""
		if player not in self._players.values() or self._game is None:
			raise TableError("unavailable")
		else:
			seat = [seat for seat, occupant in self._players.items() if occupant==player][0]
			self._game.makeCall(seat, call)
			[listener.gameCallMade(seat, call) for listener in self._listeners.values()]


	def gamePlayCard(self, player, card):
		"""Play card."""
		if identity not in self._players.values() or self._game is None:
			raise TableError("unavailable")
		else:
			seat = [seat for seat, occupant in self._players.items() if occupant==player][0]
			self._game.playCard(seat, card)
			[listener.gameCardPlayed(seat, card) for listener in self._listeners.values()]


	def gameStart(self):
		"""Instantiates game object."""
		if self._game is not None:
			raise TableError("game in progress")
		elif len([occupant for occupant in self.players.values() if occupant is not None]) < 4:
			raise TableError("seat vacant")
		else:
			deal = self._deck.generateRandom()
			self._game = Game(self._dealer, deal, vulnNS=False, vulnEW=False)
			[listener.gameStarted() for listener in self._listeners.values()]


	def removeObserver(self, identity):
		"""Removes observer from listener list.""" 
		if identity in self._players.values() and not self.inProgress():
			self.removePlayer(identity)  # Remove player first.
		if identity in self._listeners:
			del self._listeners[identity]
			[listener.observerLeave(player) for listener in self._listeners.values()]

		else:
			raise TableError("not at table")


	def removePlayer(self, player):
		"""Removes player from seat."""
		if player not in self._players.values():
			raise TableError("not at table")
		elif self.inProgress():
			raise TableError("game in progress")
		else:
			seat = [seat for seat, occupant in self._players.items() if occupant==player][0]
			self._players[seat] = None
			[listener.playerLeave(player) for listener in self._listeners.values()]


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
