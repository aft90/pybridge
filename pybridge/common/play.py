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


from call import Strain
from deck import Seat, Suit


class Trick:
	"""A trick is a dict of four cards, the leader and the trump suit."""


	def __init__(self, leader):
		assert(leader in Seat)
		self.cards  = dict.fromkeys(Seat.Seat, None)
		self.leader = leader


	def cardsPlayed(self):
		"""Returns a list of played cards."""
		return [card for card in self.cards.values() if card]


	def isComplete(self):
		"""Returns True if the trick is made."""
		return len(self.cardsPlayed()) == 4


	def playCard(self, card, seat):
		"""Add card to trick."""
		assert(card not in self.cardsPlayed())
		assert(seat in Seat)
		if not self.isComplete():
			self.cards[seat] = card


	def whoPlayed(self, card):
		"""Returns the seat from which the card was played."""
		return [seat for seat, played in self.cards.items() if played==card][0]


	def winningCard(self, trumpSuit=None):
		"""Determine which card won the trick:
		
		- In a trump contract, the highest ranked trump card wins.
		- Otherwise, the highest ranked card in the lead suit wins. 
		"""
		if self.isComplete():
			trumps = [card for card in self.cardsPlayed() if card.suit==trumpSuit]
			followers  = [card for card in self.cardsPlayed() if card.suit==self.cards[self.leader].suit]
			if len(trumps) > 0:  # Suit contract with 1+ played trumps.
				return max(trumps)  # Highest ranked trump.
			else:  # NT contract, or suit contract with no played trumps.
				return max(followers)  # Highest ranked card in lead suit.
		else:
			return False


	def winningSeat(self, trumpSuit=None):
		"""Returns the seat that played the winning card."""
		return self.whoPlayed(self.winningCard(trumpSuit))


class Play:
	"""A play represents a collection of tricks."""


	def __init__(self, declarer, trumpSuit):
		assert(declarer in Seat)
		self.declarer  = declarer
		self.tricks    = []
		assert(trumpSuit in Strain)
		self.trumpSuit = trumpSuit
		# Leader of first trick is declarer's left-hand opponent.
		self._newTrick(leader = Seat[(self.declarer.index() + 1) % 4])


	def isComplete(self):
		"""Returns true if 13 completed tricks."""
		return len(self.tricks)==13 and self._currentTrick().isComplete()


	def playCard(self, card):
		"""Plays card to current trick, assuming correct seat.

		You should check card validity with validPlay() beforehand.
		"""
		self._currentTrick().playCard(card, self.whoseTurn())
		if not self.isComplete() and self._currentTrick().isComplete():
			self._newTrick()  # Set up a new trick, if required.


	def validCard(self, card, hand, seat):
		"""Card is playable if and only if:
	
		- Play session is not complete.
		- Seat is on turn to play.
		- Card exists in hand
		- Card has not been previously played.

		In addition, if the current trick has an established lead, then
		card must follow lead suit OR hand must be void in lead suit.

		Note that specification of hand and seat is required for verification.
		"""
		if self.isComplete() or (card not in hand) or (seat is not self.whoseTurn()):
			return False
		elif self._isPlayed(card):
			return False  # Card already played on a previous trick.
		elif len(self._currentTrick().cardsPlayed()) == 0:
			return True  # Card is lead.
		else:  # Check for revoke.
			lead = self._currentTrick().cardsPlayed()[0]
			followers = [c for c in hand if c.suit==lead.suit and not self._isPlayed(c)]
			return len(followers)==0 or card in followers
			

	def whoseTurn(self, offset=0):
		"""Returns the seat that is next to play."""
		if self.isComplete():
			return False
		else:
			leaderIndex = Seat.Seat.index(self._currentTrick().leader)
			cardCount   = len(self._currentTrick().cardsPlayed())
			return Seat.Seat[(leaderIndex + cardCount + offset) % 4]


	def wonTricks(self, seat):
		"""Returns count of tricks won by seat."""
		return len([trick for trick in self.tricks if seat==trick.winningSeat(self.trumpSuit)])


	def _currentTrick(self):
		"""Returns current trick."""
		return self.tricks[-1]


	def _isPlayed(self, card):
		"""Returns trick in which card was played, False otherwise."""
		x = [trick for trick in self.tricks if card in trick.cardsPlayed()]
		return len(x)
		

	def _newTrick(self, leader=None):
		"""Adds a new trick object to self.tricks."""
		leader = leader or self._currentTrick().winningSeat()
		self.tricks.append(Trick(leader))

