# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2006 PyBridge Project.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not write to the Free Software
# Foundation Inc. 51 Franklin Street Fifth Floor Boston MA 02110-1301 USA.


from deck import Card, Deck
from bidding import Call, Bidding
from play import Trick, Play

from pybridge.strings import Error


class GameError(Exception): pass


class Game:
	"""A game."""


	def __init__(self, dealer, deal, scoring, vulnNS, vulnEW):
		"""Initialises game.

		scoring: instance of scoring class.
		"""
		self.vulnNS, self.vulnEW = vulnNS, vulnEW
		self.contract = None
		self.deal = deal
		self.bidding, self.play, self.scoring = None, None, scoring
		self._startBidding(dealer)


	def isComplete(self):
		"""Returns True if game is complete, False otherwise."""
		if self.play:
			return self.play.isComplete()
		else:
			return self.bidding.isPassedOut()


	def makeCall(self, seat, call):
		"""Makes call from seat."""
		if self.bidding.isComplete():
			raise GameError(Error.GAME_UNAVAILABLE)

		if self.bidding.whoseTurn() is not seat:
			raise GameError(Error.GAME_OUTOFTURN)
		elif not self.bidding.validCall(call):
			raise GameError(Error.GAME_INVALIDCALL)

		self.bidding.addCall(call)
			

	def playCard(self, seat, card):
		"""Plays card from seat."""
		if not self.bidding.isComplete() or self.bidding.isPassedOut():
			raise GameError(Error.GAME_UNAVAILABLE)
		elif not self.play:
			self._startPlay()  # Kickstart play session.
		elif self.play.isComplete():
			raise GameError(Error.GAME_UNAVAILABLE)

		hand = self.deal[seat]
		if self.play.whoseTurn() is not seat:
			raise GameError(Error.GAME_OUTOFTURN)
		elif not self.play.validCard(card, hand, seat):
			raise GameError(Error.GAME_INVALIDCARD)
		
		self.play.playCard(card)


	def score(self):
		"""Returns the integer score value for declarer/dummy if:

		- bidding stage has been passed out, with no bids made.
		- play stage is complete.
		"""
		if not self.isComplete():
			raise GameError(Error.GAME_UNAVAILABLE)
		elif self.bidding.isPassedOut():
			return 0  # A passed out deal does not score.
		else:
			contract = self.bidding.contract()
			declarer, dummy = contract['declarer'], Seat.Seats[(Seat.Seats.index(contract['declarer']) + 2) % 4]
			vulnerable = (self.vulnNS and declarer in (Seat.North, Seat.South)) + (self.vulnEW and declarer in (Seat.West, Seat.East))
			
			result = {'contract' : self.bidding.contract(),
			        'tricksMade' : self.play.wonTricks(declarer) + self.play.wonTricks(dummy),
			        'vulnerable' : vulnerable, }
			return self.scoring(result)


	def whoseTurn(self):
		"""Returns the seat that is next to call or play card."""
		if not self.bidding.isComplete():
			return self.bidding.whoseTurn()
		elif not self.play:
			self._startPlay()  # Kickstart play session.
		return self.play.whoseTurn()


	def _startBidding(self, dealer):
		self.bidding = Bidding(dealer)


	def _startPlay(self):
		contract  = self.bidding.contract()
		declarer  = contract['declarer']
		trumpSuit = contract['bid'].bidDenom
		self.play = Play(declarer, trumpSuit)
