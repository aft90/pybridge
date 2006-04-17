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


from bidding import Bidding
from playing import Playing

# Enumerations.
from card import Suit
from deck import Seat

from pybridge.failure import *


class Game:
	"""A game."""


	def __init__(self, dealer, deal, scoring, vulnNS, vulnEW):
		"""Initialises game.

		scoring: instance of scoring class.
		"""
		self.vulnNS, self.vulnEW = vulnNS, vulnEW
		self.contract = None
		self.deal = deal
		self.playing = None
		self.scoring = scoring
		
		# Start bidding.
		self.bidding = Bidding(dealer)


	def isComplete(self):
		"""Returns True if game is complete, False otherwise."""
		if self.playing:
			return self.playing.isComplete()
		else:
			return self.bidding.isPassedOut()


	def makeCall(self, seat, call):
		"""Makes call from seat."""
		if self.bidding.isComplete():
			raise RequestUnavailableError()
		
		if self.bidding.whoseTurn() is not seat:
			raise GameOutOfTurnError()
		elif not self.bidding.validCall(call):
			raise GameInvalidCallError()
		
		self.bidding.addCall(call)
		
		# If bidding is complete, start playing.
		if self.bidding.isComplete() and not self.bidding.isPassedOut():
			contract = self.bidding.contract()
			trumpSuit = getattr(Suit, str(contract['bid'].strain), None)  # Convert.
			self.playing = Playing(contract['declarer'], trumpSuit)


	def playCard(self, seat, card):
		"""Plays card from seat."""
		if not self.bidding.isComplete() or self.bidding.isPassedOut():
			raise RequestUnavailableError()
		elif self.playing.isComplete():
			raise RequestUnavailableError()
		
		hand = self.deal[seat]
		if self.playing.whoseTurn() is not seat:
			raise GameOutOfTurnError()
		elif not self.playing.isValidPlay(card, seat, hand):
			raise GameInvalidCardError()
		
		self.playing.playCard(card)


	def getHand(self, seat, viewer=None):
		"""Returns the hand of player specified by seat.
		
		If viewer player is specified, then the ability of viewer
		to "see" the hand will be examined.
		"""
		if viewer is None or viewer == seat:
			return self.deal[seat]  # Player can see their own hand.
		
		# During bidding, no player may see another player's hand.
		if not self.bidding.isComplete():
			raise GameHandHiddenError()
		
		# During play, the dummy player can see all hands.
		dummy = Seat[(self.playing.declarer.index + 2) % 4]
		if viewer == dummy:
			return self.deal[seat]

		# All players can see dummy's hand after first card played.
		trick = self.playing.getTrick(0)[1]
		if seat == dummy and len(trick) >= 1:
			return self.deal[seat]
		
		# Hand is not visible.
		raise GameHandHiddenError()


	def score(self):
		"""Returns the integer score value for declarer/dummy if:

		- bidding stage has been passed out, with no bids made.
		- play stage is complete.
		"""
		if not self.isComplete():
			raise RequestUnavailableError()
		elif self.bidding.isPassedOut():
			return 0  # A passed out deal does not score.
		else:
			contract = self.bidding.contract()
			declarer = contract['declarer']
			dummy = Seat[(declarer.index + 2) % 4]
			vulnerable = (self.vulnNS and declarer in (Seat.North, Seat.South)) + \
			             (self.vulnEW and declarer in (Seat.West, Seat.East))
			
			tricksMade = 0  # Count of tricks won by declarer or dummy.
			for trickindex in range(len(self.playing.winners)):
				trick = self.playing.getTrick(trickindex)
				winner = self.playing.whoPlayed(self.playing.winningCard(trick))
				trickCount += winner in (declarer, dummy)
			
			result = {'contract'   : self.bidding.contract(),
			          'tricksMade' : trickCount,
			          'vulnerable' : vulnerable, }
			return self.scoring(result)


	def whoseTurn(self):
		"""Returns the seat that is next to call or play card."""
		if not self.isComplete():
			if self.bidding.isComplete():
				return self.playing.whoseTurn()
			else:
				return self.bidding.whoseTurn()
		else:
			raise RequestUnavailableError()

