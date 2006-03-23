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


from pybridge.common.deck import Deck
from pybridge.common.enumeration import Seat
from pybridge.common.game import Game, GameError
from pybridge.common.scoring import scoreDuplicate


class BridgeTable:
	"""A bridge table sits four players."""
	# TODO: perhaps subclass BridgeTable and facilitate tables for different card games.


	def __init__(self, name):
		self.dealer   = Seat.North  # Rotate around the table for each deal.
		self.deck     = Deck()
		self.game     = None
		self.name     = name
		self.observers = {}  # For each watching user name, its Listener object.
		self.players  = dict.fromkeys(Seat.Seats, None)
		self.scoring  = scoreDuplicate  # A function.


	def playerAdd(self, username, seat):
		"""Allocates seat to player if:
		
		- player is watching the table.
		- player is not already playing at the table.
		- the specified seat is empty.
		"""
		if username not in self.observers:
			return "not watching table"
		elif username in self.players.values():
			return "alredy playing at table"
		elif self.players[seat] is not None:
			return "seat occupied"
		else:
			self.players[seat] = username
			self.informWatchers("playerJoins", username, seat)
		# TODO: find somewhere better to put this code.
		if game is None:
			playerCount = len([p for p in self.players.values() if p != None])
			if playerCount == 4:
				self.gameStart()


	def playerRemove(self, username):
		"""Removes player from seat."""
		if username in self.players.values():
			seat = [seat for seat, username in self.players.items() if player==username][0]
			self.players[seat] = None
			self.informWatchers("playerLeaves", username, seat)
		else:
			return "cannot remove player"


	def gameStart(self, dealer=None, deal=None):
		"""Called to start a game."""
		deal = deal or self.deck.dealRandom()
		self.dealer = dealer or Seat.Seats[(Seat.Seats.index(self.declarer) + 1) % 4]
		self.game = Game(self.dealer, deal, self.scoring, vulnNS=False, vulnEW=False)
		self.informWatchers("gameStarted")


	def gameEnd(self):
		"""Called to terminate a game, when:
		
		- the bidding has been passed out without a contract.
		- the play has been completed.
		"""
		# TODO: get score.
		self.informWatchers("gameFinished")
		self.game = None


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
			return "hand hidden"
		else:
			return "unavailable"


	def gameMakeCall(self, player, call):
		"""Player makes call."""
		seat = self.getSeatForPlayer(player)
		if not seat:  # Invalid player.
			return "unavailable"
		try:
			self.game.makeCall(seat, call)
			self.informWatchers("gameCallMade", seat, call)
			# Check for contract or end of game.
			if self.game.bidding.isPassedOut():
				self.gameEnd()
			elif self.game.bidding.isComplete():
				contract = "wibble"
				self.informWatchers("gameContract", contract)
		except GameError, error:
			return error


	def gamePlayCard(self, player, card):
		"""Player plays card."""
		if player not in self.players.values() or self.game is None:
			return "unavailable"
		try:
			seat = self.getSeat(player)
			self.game.playCard(seat, card)
			self.informWatchers("gameCardPlayed", seat, card)
			# Check for end of game.
			if self.game.play.isComplete():
				self.gameEnd()
		except GameError, error:
			return error


	def gameTurn(self):
		"""Return the seat that is next to play."""
		if self.game:
			return self.game.whoseTurn()
		else:
			return "unavailable"


# Utility functions.


	def getSeatForPlayer(self, username):
		"""Returns seat of player username, or None."""
		return ([seat for seat, player in self.players.items() if player==username] or [None])[0]


	def informWatchers(self, eventName, *args):
		"""For each given user, calls specified event with provided args."""
		for observer in self.observers.values():
			event = getattr(observer, eventName)
			event(*args)
