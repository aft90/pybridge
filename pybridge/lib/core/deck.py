

class Card:
	"""
	Initialises a card object with rank, suit and available flag.
	"""
	rankNames = {2 : 'Two', 3 : 'Three', 4 : 'Four', 5 : 'Five', 6 : 'Six',
	             7 : 'Seven', 8 : 'Eight', 9 : 'Nine', 10 : 'Ten',
	             11 : 'Jack', 12 : 'Queen', 13 : 'King', 14 : 'Ace'}
	suitNames = {'c' : 'Club', 'd' : 'Diamond', 'h' : 'Heart', 's' : 'Spade'}
	
	def __init__(self, rank, suit):
		if rank in range(2, 15): self.rank = rank
		else: raise 'Bad specification of rank'
		if suit in self.suitNames: self.suit = suit
		else: raise 'Bad specification of suit'
		self.isAvailable = True
	
	def __str__(self):
		return self.rankNames[self.rank] + " of " + self.suitNames[self.suit] + "s"

class Hand:
	"""
	Initialises a hand object with an empty card list.
	"""
	
	def __init__(self):
		self.cards = []
	
	def addCard(self, card):
		if card not in self.cards:
			self.cards.append(card)
			return True
		else: return False
	
	def removeCard(self, card):
		if card in self.cards:
			self.cards.remove(card)
			return True
		else: return False
	
	def numCards(self):
		return len(self.cards)
	
	def isValid(self):
		"""Is the hand valid?"""
		if numCards == 13: return True
		else: return False
	
	def evaluate(self):
		# This procedure should be moved to the ACOL player class!
		evaluation = 0
		suitcount = {'c' : 0, 'd' : 0, 'h' : 0, 's' : 0}
		for card in self.cards:
			if card.rank > 10:
				evaluation += card.rank - 10
			suitcount[card.suit] += 1
		for suit in suitcount:
			if suitcount[suit] < 3:
				evaluation += 2 - suitcount[suit]
		return evaluation

class Deck:
	"""
	Initialises a deck object with 52 card objects and 4 hand objects.
	"""
	suitOrder = ['c', 'd', 'h', 's']
	
	def __init__(self):
		self.cards = []
		for suit in self.suitOrder:
			for rank in range(2,15):
				self.cards.append(Card(rank, suit))
		self.hands = {'n' : Hand(), 's' : Hand(), 'w' : Hand(), 'e' : Hand()}
	
	def deal(self):
		"""
		Shuffles the card object elements in the deck card list.
		Deals 13 cards to each of the 4 hands.
		"""
		if self.cards:
			for handid, hand in self.hands.items():
				for i in range(13):
					hand.addCard(self.cards.pop())
			return True
		else: return False
	
	def shuffle(self):
		import random
		random.shuffle(self.cards)
