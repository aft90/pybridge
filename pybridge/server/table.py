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
from pybridge.common.game import Game, GameError
from pybridge.common.scoring import scoreDuplicate

# Enumerations.
from pybridge.common.deck import Seat

from pybridge.strings import Event, Error


class TableError(Exception): pass


class BridgeTable:
	"""A bridge table sits four players."""
	# TODO: perhaps subclass BridgeTable, facilitating tables for different card games.


	def __init__(self, name):
		self.dealer   = Seat.North  # Rotate around the table for each deal.
		self.deck     = Deck()
		self.game     = None
		self.name     = name
		self.observers = {}  # For each watching user name, its Listener object.
		self.players  = dict.fromkeys(Seat, None)
		self.scoring  = scoreDuplicate  # A function.


	def playerAdd(self, username, seat):
		"""Allocates seat to player if:
		
		- player is watching the table.
		- player is not already playing at the table.
		- the specified seat is empty.
		"""
		if username not in self.observers:	# Not watching table.
			raise TableError(Error.COMMAND_UNAVAILABLE)
		elif username in self.players.values():	# Already playing at table.
			raise TableError(Error.COMMAND_UNAVAILABLE)
		elif self.players[seat] is not None:	# Seat occupied.
			raise TableError(Error.COMMAND_UNAVAILABLE)
		else:
			self.players[seat] = username
			self.informWatchers(Event.TABLE_PLAYERSITS, username, seat)
		# TODO: find somewhere better to put this code.
		if self.game is None:
			playerCount = len([p for p in self.players.values() if p != None])
			if playerCount == 4:
				self.gameStart()


	def playerRemove(self, username):
		"""Removes player from seat."""
		if username not in self.players.values():
			raise TableError(Error.COMMAND_UNAVAILABLE)
		else:
			seat = self.getSeatForPlayer(username)
			self.players[seat] = None
			self.informWatchers(Event.TABLE_PLAYERSTANDS, username, seat)


	def gameStart(self, dealer=None, deal=None):
		"""Called to start a game."""
		deal = deal or self.deck.dealRandom()
		self.dealer = dealer or Seat[(self.dealer.index + 1) % 4]
		self.game = Game(self.dealer, deal, self.scoring, vulnNS=False, vulnEW=False)
		self.informWatchers(Event.GAME_STARTED)


	def gameEnd(self):
		"""Called to terminate a game, when:
		
		- the bidding has been passed out without a contract.
		- the play has been completed.
		"""
		# TODO: get score.
		self.informWatchers(Event.GAME_FINISHED)
		self.game = None


	def gameGetHand(self, seat, viewpoint=None):
		"""Returns the hand of seat, or False if hand is unavailable or hidden.

		If viewing player's seat is specified, then that player's ability to
		view the hand of seat will be examined.
		"""
		if self.game:
			if viewpoint in (seat, None):
				# No viewpoint specified, or viewpoint is seat.
				return self.game.deal[seat]
			# We now consider viewpoint, provided that bidding is complete.
			if self.game.bidding.isComplete():
				dummy = Seat[(self.game.play.declarer.index + 2) % 4]
				if viewpoint is dummy:
					# Dummy can see all hands in play.
					return self.game.deal[seat]
				elif seat is dummy and self.game.play.tricks[0].cardsPlayed() > 0:
					# Declarer and defenders can see dummy's hand after first card is played.
					return self.game.deal[seat]
			raise TableError(Error.GAME_UNAVAILABLE)  # Hidden hand.
		else:
			raise TableError(Error.COMMAND_UNAVAILABLE)


	def gameMakeCall(self, player, call):
		"""Player makes call."""
		seat = self.getSeatForPlayer(player)
		if not seat:  # Invalid player.
			raise TableError(Error.COMMAND_UNAVAILABLE)

		try:  # Trap a GameError.
			self.game.makeCall(seat, call)
		except GameError, error:
			raise TableError(error)

		self.informWatchers(Event.GAME_CALLMADE, seat, call)
		# Check for contract or end of game.
		if self.game.bidding.isPassedOut():
			self.gameEnd()
		elif self.game.bidding.isComplete():
			contract = self.game.bidding.contract()
			self.informWatchers(Event.GAME_CONTRACTAGREED, contract)


	def gamePlayCard(self, player, card):
		"""Player plays card."""
		if player not in self.players.values() or self.game is None:
			raise TableError(Error.COMMAND_UNAVAILABLE)
		seat = self.getSeatForPlayer(player)
		try:
			self.game.playCard(seat, card)
			self.informWatchers(Event.GAME_CARDPLAYED, seat, card)
			# Check for end of game.
			if self.game.play.isComplete():
				self.gameEnd()
		except GameError, error:
			raise TableError(error)


	def gameTurn(self):
		"""Return the seat that is next to play."""
		if self.game:
			return self.game.whoseTurn()
		else:
			raise TableError(Error.COMMAND_UNAVAILABLE)


# Utility functions.


	def getSeatForPlayer(self, username):
		"""Returns seat of player username, or None."""
		return ([seat for seat, player in self.players.items() if player==username] or [None])[0]


	def informWatchers(self, eventName, *args):
		"""For each given user, calls specified event with provided args."""
		for observer in self.observers.values():
			event = getattr(observer, eventName)
			event(*args)
