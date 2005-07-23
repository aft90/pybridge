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


class Hand(list):


	def isValid(self):
		"""Is the hand valid?"""
		return len(self) == 13


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


	def countSuits(self):
		"""Returns a dictionary of suits with a count of cards in each suit."""
		suitCount = dict.fromkeys(Suit.Suits, 0)
		for card in self:
			suitCount[card.suit] += 1
		return suitCount


class Deck:


	def __init__(self):
		"""Initialises a deck object with 52 card objects."""
		self._cards = []
		for suit in Suit.Suits:
			for rank in Rank.Ranks:
				self._cards.append(Card(rank, suit))


	def reset(self):
		self._deal = {Seat.North : Hand(), Seat.South : Hand(), Seat.East : Hand(), Seat.West : Hand()}


	def deal(self):
		"""Deals 13 cards to each of the 4 hands."""
		self.reset()
		index = 0
		for hand in self._deal.values():
			while not hand.isValid():
				hand.addCard(self._cards[index])
				index += 1
			hand.sort()
		return self._deal


	def shuffle(self):
		"""Shuffles the cards."""
		import random
		random.shuffle(self._cards)
