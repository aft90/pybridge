from enumeration import Rank, Suit, Seat


class Card:


	def __init__(self, rank, suit):
		"""Initialises a card object with rank, suit and played flag."""
		if rank in Rank.Ranks and suit in Suit.Suits:
			self.rank, self.suit = rank, suit
		else:
			raise "Invalid specification of card."


	def __eq__(self, other):
		"""Two cards are equivalent if they have the same rank and suit."""
		return (self.suit == other.suit) and (self.rank == other.rank)


	def __cmp__(self, other):
		"""Compare cards for hand sorting."""
		selfIndex = (Suit.Suits.index(self.suit) * 13) + Rank.Ranks.index(self.rank)
		otherIndex = (Suit.Suits.index(other.suit) * 13) + Rank.Ranks.index(other.rank)
		return cmp(selfIndex, otherIndex)


	def __str__(self):
		"""Returns the English name for the card."""
		return self.rank + " of " + self.suit + "s"


class Hand(list):


	def addCard(self, card):
		"""Adds a specified card to the hand."""
		if card not in self and len(self) < 13:
			self.append(card)
			return True
		else:
			return False


	def removeCard(self, card):
		"""Removes a specified card from the hand."""
		if card in self:
			self.remove(card)
			return True
		else:
			return False


class Deck:


	import random


	def __init__(self):
		"""Initialises a deck object with 52 card objects."""
		self._cards = []
		for suit in Suit.Suits:
			for rank in Rank.Ranks:
				self._cards.append(Card(rank, suit))


	def _build(self):
		"""Returns a dictionary of hands."""
		return {Seat.North : Hand(), Seat.South : Hand(), Seat.East : Hand(), Seat.West : Hand()}


	def generateOrdered(self, combination):
		"""Returns a deal, determined by combination."""
		pass  # NOT IMPLEMENTED YET.
	

	def generateRandom(self):
		"""Returns a deal, from a shuffled deck."""
		self.shuffle()
		hands = self._build()
		for index, card in enumerate(self._cards):
			hands[Seat.Seats[index/13]].addCard(card)
		return hands
		

	def shuffle(self):
		"""Shuffles the cards."""
		import random
		random.shuffle(self._cards)
