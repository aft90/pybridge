from enumeration import Seat, Suit


class Trick:
	"""A trick is a list of four cards, the leader and the trump suit."""


	def __init__(self, leader, trumpSuit):
		self.cards = []
		self.leader = leader
		self.trumpSuit = trumpSuit


	def isMade(self):
		"""Returns true if the trick is made."""
		return len(self.cards) == 4


	def validCard(self, card, hand):
		"""Card is playable in this trick if and only if:
		
		- Card is lead.
		- Trick is not complete.
		- Card suit is lead suit, or hand is void in lead suit.
		"""
		if len(self.cards) == 0:
			return True  # Card is lead.
		elif self.isMade() or card in self.cards:
			return False
		else:
			leadSuit = self.cards[0].suit
			return card.suit == leadSuit or hand.countSuits()[leadSuit] == 0


	def playCard(self, card, hand):
		"""If card is valid, add card to trick."""
		if self.validCard(card, hand):
			self.cards.append(card)
			return True
		else:
			return False


	def whoseTurn(self):
		"""Returns the seat that is next to play."""
		return Seat.Seats[(len(self.cards) + Seat.Seats.index(self.leader)) % 4]


	def whoPlayed(self, card):
		"""Returns the seat from which the card was played."""
		if card in self.cards:
			return Seat.Seats[(self.cards.index(card) + Seat.Seats.index(self.leader)) % 4]
		else:
			return False


	def whoWon(self):
		"""Returns the seat that played the winning card."""
		if self.isMade():
			return self.whoPlayed(card = self.winningCard())
		else:
			return False


	def winningCard(self):
		"""Determine which card won the trick:
		
		- In a trump contract, the highest ranked trump card wins.
		- Otherwise, the highest ranked card in the lead suit wins. 
		"""
		if self.isMade():
			trumps = [card for card in self.cards if card.suit==self.trumpSuit]
			if self.trumpSuit in Suit.Suits and len(trumps) > 0:
				return max(trumps)  # Highest ranked trump.
			else:
				followers = [card for card in self.cards if card.suit==self.cards[0].suit]
				return max(followers)  # Highest ranked card in lead suit.
		else:
			return False

				
class Play:
	""" A play represents a collection of tricks. """


	def __init__(self, hands, declarer, trumpSuit):
		self.hands = hands
		self.trumpSuit = trumpSuit
		self.tricks = []
		self.declarer = declarer
		self.dummy = Seat.Seats[(Seat.Seats.index(self.declarer) + 2) % 4]
		# Add first trick to trick list: allows for tidier code.
		self.tricks.append(Trick(self.declarer, self.trumpSuit))


	def currentTrick(self):
		if self.tricks:
			return self.tricks[-1]
		else:
			return False


	def isComplete(self):
		"""Returns true if play is complete. (13 completed tricks)"""
		return len(self.tricks) == 13 and self.currentTrick().isMade()


	def newTrick(self):	
		"""Adds a new trick object to the tricks list if:
		
		- Play is not complete.
		- The current trick is complete.
		"""
		if not self.isComplete() and self.currentTrick().isMade():
			leader = self.currentTrick().whoWon()
			self.tricks.append(Trick(leader, self.trumpSuit))
			return True
		else: return False


	def wonTricks(self, seats):
		"""Returns a list of tricks won by members of seats."""
		if self.isComplete:
			return [trick for trick in self.tricks if trick.whoWon() in seats]
		else:
			return False
