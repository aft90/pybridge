from enumeration import Seat, Suit

class Trick:
	"""
	A trick is a list of four cards, the leader and the trump suit.
	"""
	seatOrder = [Seat.North, Seat.East, Seat.South, Seat.West]

	def __init__(self, leader, trumpSuit):
		self.cards = []
		self.leader = leader
		self.trumpSuit = trumpSuit
	
	def isMade(self):
		""" Returns true if the trick is made. """
		return len(self.cards) == 4
	
	def validCard(self, card, hand):
		"""
		Card is playable in this trick if and only if:
		- Trick is not complete.
		- Card is not marked as played.
		- Card suit equals lead suit, or hand is void in lead suit.
		"""
		if not self.isMade() and not card.isPlayed:
			try:
				leadSuit = self.cards[0].suit
				if card.suit == leadSuit or hand.countSuits()[leadSuit] == 0:
					return True
			except IndexError:
				# No cards played in trick: this is lead card.
				return True
		return False
		
	def playCard(self, card, hand):
		""" If card is valid, add card to trick and set card played flag. """
		if self.validCard(card, hand):
			self.cards.append(card)
			card.isPlayed = True
			return True
		else: return False
	
	def whoseTurn(self):
		return self.seatOrder[(len(self.cards) + self.seatOrder.index(self.leader)) % 4]
	
	def whoPlayed(self, card):
		""" Return the seat from which the card was played. """
		if card in self.cards:
			return self.seatOrder[(self.cards.index(card) + self.seatOrder.index(self.leader)) % 4]
		else: return False
			
	def whoWon(self):
		""" Return the seat which played the winning card. """
		if self.isMade():
			return self.whoPlayed(card = self.winningCard())
		else: return False
		
	def winningCard(self):
		"""
		Determine which card won the trick:
		- In a trump contract, the highest ranked trump card wins.
		- Otherwise, the highest ranked card in the lead suit wins. 
		"""
		if self.isMade():
			topCard = self.cards[0]
			for card in self.cards[1:]:
				# Is the top card a trump?
				if topCard.suit == self.trumpSuit:
					# Am I a trump and am I higher ranked than topCard?
					if card.suit == self.trumpSuit and card.rank > topCard.rank:
						topCard = card
				else:
					# Am I a trump?
					if card.suit == self.trumpSuit:
						topCard = card
					# Am I of the same suit as topCard and I higher ranked than topCard?
					elif card.suit == topCard.suit and card.rank > topCard.rank:
						topCard = card
			return topCard
		else: return False

class Play:
	""" A play represents a collection of tricks. """
	
	seatOrder = [Seat.North, Seat.East, Seat.South, Seat.West]
	
	def __init__(self, hands, declarer, trumpSuit):
		self.hands = hands
		self.trumpSuit = trumpSuit
		self.tricks = []
		self.declarer = declarer
		self.dummy = self.seatOrder[(self.seatOrder.index(self.declarer) + 2) % 4]
		# Add first trick to trick list
		self.tricks.append(Trick(self.declarer, self.trumpSuit))
	
	def isComplete(self):
		""" Returns true if play is complete (13 completed tricks).	"""
		return len(self.tricks) == 13 and self.currentTrick().isMade()
	
	def currentTrick(self):
		if self.tricks: return self.tricks[-1]
		else: return False

	def newTrick(self):	
		"""
		Adds a new trick object to the tricks list if:
			Play is not complete.
			The current trick (if it exists) must be complete.
		"""
		if not self.isComplete() and self.currentTrick().isMade():
			leader = self.currentTrick().whoWon()
			self.tricks.append(Trick(leader, self.trumpSuit))
			return True
		else: return False
	
	def listWonTricks(self):
		""" Returns a list of tricks won by declarer or dummy. """
		if self.isComplete:
			wonTricks = []
			for trick in self.tricks:
				if trick.whoWon() in [self.declarer, self.dummy]:
					wonTricks.append(trick)
			return wonTricks
		else: return False
	
	def countWonTricks(self):
		""" Returns a count of the tricks won by declarer or dummy.	"""
		if self.isComplete(): return len(self.listWonTricks())
		else: return False
