from enumeration import Rank, Suit, Seat

class Card:
	
	def __init__(self, rank, suit):
		""" Initialises a card object with rank, suit and played flag. """
		if rank in Rank.Ranks: self.rank = rank
		else: raise 'Bad specification of rank.'
		if suit in Suit.Suits: self.suit = suit
		else: raise 'Bad specification of suit.'
		self.isPlayed = False  # ugh, required by play class (for now)
	
	def __eq__(self, other):
		""" Two cards are equivalent if they have the same rank and suit. """
		return (self.suit == other.suit) and (self.rank == other.rank)
	
	def __cmp__(self, other):
		""" Compare cards for hand sorting. """
		selfStrength = (Suit.Suits.index(self.suit) * 13) + Rank.Ranks.index(self.rank)
		otherStrength = (Suit.Suits.index(other.suit) * 13) + Rank.Ranks.index(other.rank)
		return cmp(selfStrength, otherStrength)
	
class Hand:
	
	def __init__(self):
		""" Initialises a hand object with an empty card list. """
		self.cards = []
	
	def isValid(self):
		""" Is the hand valid? """
		return self.countCards() == 13

	def addCard(self, card):
		""" Adds a specified card to the hand. """
		if card not in self.cards:
			self.cards.append(card)
			return True
		else: return False
	
	def removeCard(self, card):
		""" Removes a specified card from the hand. """
		if card in self.cards:
			self.cards.remove(card)
			return True
		else: return False
	
	def countCards(self):
		""" Returns a count of card elements in hand. """
		return len(self.cards)
	
	def countSuits(self):
		""" Returns a dictionary of suits with their respective card counts. """
		suitCount = {Suit.Club : 0, Suit.Diamond : 0, Suit.Heart : 0, Suit.Spade : 0}
		for card in self.cards:
			suitCount[card.suit] += 1
		return suitCount
	
class Deck:
	
	def __init__(self):
		""" Initialises a deck object with 52 card objects. """
		self.cards = []
		for suit in Suit.Suits:
			for rank in Rank.Ranks:
				self.cards.append(Card(rank, suit))
	
	def reset(self):
		self.hands = {Seat.North : Hand(), Seat.South : Hand(), Seat.East : Hand(), Seat.West : Hand()}
	
	def deal(self):
		""" Deals 13 cards to each of the 4 hands. """
		self.reset()
		card = 0
		for hand in self.hands.values():
			while not hand.isValid():
				hand.addCard(self.cards[card])
				card += 1
	
	def shuffle(self):
		""" Shuffles the card object elements in the deck card list. """
		import random
		random.shuffle(self.cards)
