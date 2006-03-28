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


import random  # To shuffle a deck.

from pybridge.enum import Enum

Rank = Enum('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
             'Ten', 'Jack', 'Queen', 'King', 'Ace')

Seat = Enum('North', 'East', 'South', 'West')  # Clockwise.

Suit = Enum('Club', 'Diamond', 'Heart', 'Spade')


class Card:
	"""A card has a rank and a suit."""

	def __init__(self, rank, suit):
		assert(rank in Rank)
		assert(suit in Suit)
		self.rank = rank
		self.suit = suit


	def __eq__(self, other):
		"""Two cards are equivalent if they have the same rank and suit."""
		assert(isinstance(other, Card))
		return self.suit == other.suit and self.rank == other.rank


	def __cmp__(self, other):
		"""Compare cards for hand sorting.
		
		Care must be taken when comparing cards of different suits.
		
		pre:
			isinstance(other, Card)
		"""
		assert(isinstance(other, Card))
		selfIndex = self.suit.index*13 + self.rank.index
		otherIndex = other.suit.index*13 + other.rank.index
		return cmp(selfIndex, otherIndex)


	def __str__(self):
		"""Returns the English name for the card."""
		return self.rank + " of " + self.suit + "s"


class Deck:
	"""A deck consists of 52 cards.

	inv:
		len(self.cards) == len(Rank) * len(Suit)
	"""

	def __init__(self):
		self.cards = []
		for suit in Suit:
			for rank in Rank:
				self.cards.append(Card(rank, suit))


	def dealOrdered(self, combination):
		"""Returns a deal, ordered by combination."""
		pass  # Not implemented yet.


	def dealRandom(self):
		"""Returns a deal, from a shuffled deck."""
		random.shuffle(self.cards)
		hands = {Seat.North : [],
		         Seat.East  : [],
		         Seat.South : [],
		         Seat.West  : [], }
		for index, card in enumerate(self.cards):
			hands[Seat[index % len(Seat)]].append(card)
		return hands

