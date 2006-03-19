from enumeration import Rank, Suit, Seat
import random  # To shuffle a deck.


class Card:
	"""A card has a rank and a suit."""


	def __init__(self, rank, suit):
		"""
		pre:
			rank in Rank.Ranks
			suit in Suit.Suits
		"""
		self.rank = rank
		self.suit = suit


	def __eq__(self, other):
		"""Two cards are equivalent if they have the same rank and suit.
		
		pre:
			isinstance(other, Card)
		"""
		return (self.suit == other.suit) and (self.rank == other.rank)


	def __cmp__(self, other):
		"""Compare cards for hand sorting.
		
		pre:
			isinstance(other, Card)
		"""
		selfIndex = (Suit.Suits.index(self.suit) * 13) + Rank.Ranks.index(self.rank)
		otherIndex = (Suit.Suits.index(other.suit) * 13) + Rank.Ranks.index(other.rank)
		return cmp(selfIndex, otherIndex)


	def __str__(self):
		"""Returns the English name for the card."""
		return self.rank + " of " + self.suit + "s"


# TODO: check that we really don't need this class, and remove it entirely.
#class Hand(list):
#
#
#	def addCard(self, card):
#		"""Adds a specified card to the hand."""
#		if card not in self and len(self) < 13:
#			self.append(card)
#			return True
#		else:
#			return False
#
#
#	def removeCard(self, card):
#		"""Removes a specified card from the hand."""
#		if card in self:
#			self.remove(card)
#			return True
#		else:
#			return False


class Deck:
	"""A deck consists of 52 cards.

	inv:
		len(self.cards) == 52
	"""

	def __init__(self):
		self.cards = []
		for suit in Suit.Suits:
			for rank in Rank.Ranks:
				self.cards.append(Card(rank, suit))


	def dealOrdered(self, combination):
		"""Returns a deal, determined by combination."""
		pass  # NOT IMPLEMENTED YET.
	

	def dealRandom(self):
		"""Returns a deal, from a shuffled deck."""
		self.shuffle()
		hands = {
			Seat.North : [],
			Seat.South : [],
			Seat.East  : [],
			Seat.West  : [],
		}
		for index, card in enumerate(self.cards):
			hands[Seat.Seats[index/13]].append(card)
		return hands
		

	def shuffle(self):
		"""Shuffles the cards."""
		random.shuffle(self.cards)
