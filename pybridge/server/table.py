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


from pybridge.common.deck import Deck
from pybridge.common.enumeration import Seat
from pybridge.common.game import Game, GameError
from pybridge.common.scoring import scoreDuplicate


class TableError(Exception): pass


class BridgeTable:
	"""A bridge table sits four players."""
	# TODO: perhaps subclass BridgeTable and facilitate tables for different card games.


	def __init__(self, tablename):
		self.dealer    = Seat.North  # Rotate around the table for each deal.
		self.deck      = Deck()
		self.game      = None
		self.name      = tablename
		self.scoring   = scoreDuplicate  # A function!
		
		self.listeners = {}  # For each watching username, its TableListener object.
		self.players   = dict.fromkeys(Seat.Seats, None)


	def getSeatForPlayer(self, username):
		"""Returns seat of player username, or None."""
		return ([seat for seat, player in self.players.items() if player==username] or [None])(0)


	def playerAdd(self, username, seat):
		"""Allocates seat to player if:

		- player is not already playing at the table.
		- the specified seat is empty.
		"""
		if username in self.listeners and self.players[seat] is None:
			self.players[seat] = username
			[listener.playerJoins(username, seat) for listener in self.listeners.values()]
		else:
			raise TableError("cannot add player")


	def playerRemove(self, username):
		"""Removes player from seat."""
		if username in self.players.values():
			seat = [seat for seat, username in self.players.items() if player==username][0]  # Get key.
			self.players[seat] = None
			[listener.playerLeaves(username, seat) for listener in self.listeners.values()]
		else:
			raise TableError("cannot remove player")


	def gameStart(self):
		"""Called to start a game."""
		deal = self.deck.dealRandom()
		self.game = Game(self.dealer, deal, self.scoring, vulnNS=False, vulnEW=False)
		[listener.gameStarted() for listener in self.listeners.values()]


	def gameFinished(self):
		"""Called when a game has finished:
		
		- the bidding has been passed out without a contract.
		- the play has been completed.
		"""
		# TODO: get score.
		self.game = None
		[listener.gameFinished() for listener in self.listeners.values()]


	def gameHand(self, seat, player=None):
		"""Returns the hand of seat, or False if hand is unavailable or hidden.

		If player is specified, then that player's ability to view the hand of
		seat will be examined.
		"""
		if self.game:
			viewpoint = self.getSeatForPlayer(username)
			if viewpoint in (seat, None):
				# No viewpoint specified, or viewpoint is seat.
				return self.game.deal[seat]
			# We now consider viewpoint, provided that bidding is complete.
			if self.game._getStage() != 'bidding':
				dummy = Seat.Seats[(Seat.Seats.index(self.game.play.declarer) + 2) % 4]
				if viewpoint is dummy:
					# Dummy can see all hands in play.
					return self.game.deal[seat]
				elif seat is dummy and self.game.play.tricks[0].cardsPlayed() > 0:
					# Declarer and defenders can see dummy's hand after first card is played.
					return self.game.deal[seat]
			raise TableError("hand hidden")
		else:
			raise TableError("unavailable")


	def gameMakeCall(self, player, call):
		"""Player makes call."""
		seat = self.getSeatForPlayer(player)
		if not seat:  # Invalid player.
			raise TableError("unavailable")
		try:
			self.game.makeCall(seat, call)
			[listener.gameCallMade(seat, call) for listener in self.listeners.values()]
			# Check for contract or end of game.
			if self.game.bidding.isPassedOut():
				self.gameFinished()
			elif self.game.bidding.isComplete():
				contract = "wibble"
				[listener.gameContract(contract) for listener in self.listeners.values()]
		except GameError:
			return TableError(error)


	def gamePlayCard(self, player, card):
		"""Player plays card."""
		if player not in self.players.values() or self.game is None:
			raise TableError("unavailable")
		try:
			seat = self.getSeat(player)
			self.game.playCard(seat, card)
			[listener.gameCardPlayed(seat, card) for listener in self.listeners.values()]
			# Check for end of game.
			if self.game.play.isComplete():
				self.gameFinished()
		except GameError, error:
			return TableError(error)


	def gameTurn(self):
		"""Return the seat that is next to play."""
		if self.game:
			return self.game.whoseTurn()
		else:
			raise TableError("unavailable")
