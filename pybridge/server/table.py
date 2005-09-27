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


from lib.core.deck import Deck
from lib.core.enumeration import Seat
from lib.core.game import Game, GameError
from lib.core.scoring import scoreDuplicate


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
		self._scoring   = scoreDuplicate  # A function!


	def inProgress(self):
		"""Returns True if game in progress."""
		if self._game and len([player for player in self._players.values() if player is not None]) == 4:
			return not self._game.isComplete()


	def isObserver(self, identifier):
		"""Returns True if user is observing this table."""
		return identifier in self._listeners and identifier not in self._players.values()


	def isPlayer(self, identifier):
		"""Returns True if user is playing this table."""
		return identifier in self._players.values()


	def getPlayer(self, seat):
		"""Returns player at seat."""
		return self._players[seat] or None


	def getSeat(self, player):
		"""Returns seat of player"""
		if player in self._players.values():
			return [seat for seat, occupant in self._players.items() if occupant is player][0]
		else:
			raise TableError("player not at table")


	def addObserver(self, observer, listener):
		"""Adds listener object as table observer."""
		if observer in self._listeners:
			raise TableError("already at table")
		else:
			self._listeners[observer] = listener
			[listener.observerJoins(observer) for listener in self._listeners.values()]
			

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
		self._players[seat] = player
		[listener.playerJoins(player) for listener in self._listeners.values()]
		if not self.inProgress():
			self._gameDeal()


	def gameHand(self, seat, position=None):
		"""Returns the hand of the player occupying seat::Seat.

		If position::Seat is specified, and the player at position may not view
		the hand of the player at seat, then an error will be raised.
		"""
		if not self.inProgress():
			raise TableError("unavailable")
		# Check for peeking at other players' hands.
		if position not in (seat, None):
			stage = self._game._getStage()
			if stage is 'bidding':
				raise TableError("hand not visible")
			elif stage is 'play':
				# Note that, as dummy does not take part in play, he may view all hands.
				declarer = self._game.play.declarer
				dummy = Seat.Seats[(Seat.Seats.index(declarer) + 2) % 4]
				if position is declarer:
					# Declarer can only see his and dummy's hands.
					if seat not in (declarer, dummy):
						raise TableError("hand not visible")
				elif position is not dummy:  # (defender)
					if seat is not dummy:
						raise TableError("hand not visible")
					# Defenders can see dummy's hand, only after the first card is played.
					elif self._game.play.tricks[0].cardsPlayed() == 0:  # (seat is dummy)
						raise TableError("hand not visible")
		# If we get this far, return the requested hand.
		return self._game.deal[seat]


	def gameMakeCall(self, player, call):
		"""Make call."""
		if player not in self._players.values() or self._game is None:
			raise TableError("unavailable")
		seat = self.getSeat(player)
		try:
			self._game.makeCall(seat, call)
			[listener.gameCallMade(seat, call) for listener in self._listeners.values()]
			self._checkContract()
			self._checkResult()
		except GameError, error:
			raise TableError(error)


	def gamePlayCard(self, player, card):
		"""Play card."""
		if player not in self._players.values() or self._game is None:
			raise TableError("unavailable")
		seat = self.getSeat(player)
		try:
			self._game.playCard(seat, card)
			[listener.gameCardPlayed(seat, card) for listener in self._listeners.values()]
			self._checkResult()
		except GameError, error:
			raise TableError(error)


	def gameTurn(self):
		"""Return the seat that is next to play."""
		if not self.inProgress():
			raise TableError("unavailable")
		return self._game.whoseTurn()


	def removeObserver(self, observer):
		"""Removes observer from listener list."""
		if observer in self._players.values():
			self.removePlayer(identity)  # Remove player first.
		if observer in self._listeners:
			del self._listeners[observer]
			[listener.observerLeaves(observer) for listener in self._listeners.values()]
			# TODO: Check if the table should be closed down. Can't use registry.
		else:
			raise TableError("not at table")


	def removePlayer(self, player):
		"""Removes player from seat."""
		if player not in self._players.values():
			raise TableError("not at table")
		else:
			seat = self.getSeat(player)
			self._players[seat] = None
			[listener.playerLeaves(player) for listener in self._listeners.values()]


	def _checkContract(self):
		"""Checks for game contract. Informs listeners."""
		contract = self._game.bidding.contract()
		if contract:
			[listener.gameContract(contract) for listener in self._listeners.values()]


	def _checkResult(self):
		"""Checks for game result. Informs listeners."""
		if self._game.isComplete():
			result = self._game.score()
			[listener.gameResult(result) for listener in self._listeners.values()]


	def _gameDeal(self):
		"""Instantiates game object."""
		deal = self._deck.generateRandom()
		self._game = Game(self._dealer, deal, self._scoring, vulnNS=False, vulnEW=False)
