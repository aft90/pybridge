class Trick:
	"""
	A trick is a list of four cards, the leader and the trump suit.
	"""

	def __init__(self, leader, trumpSuit):
		self.cards = []
		self.leader = leader
		self.trumpSuit = trumpSuit
	
	def isComplete(self):
		return len(self.cards) == 4
	
	def playCard(self, card):
		"""
		If card is available and trick is not complete, play card.
		"""
		if card.isAvailable and not self.isComplete():
			card.isAvailable = False
			self.cards.append(card)
			return True
		else:
			return False
	
	def whoPlayed(self, card):
		if card in self.cards:
			thing = ['n', 'e', 's', 'w']
			return thing[(self.cards.index(card) + thing.index(self.leader)) % 4]
		else: return False
			
	def whoWon(self):
		"""
		The winner played the winning card.
		"""
		if self.isComplete():
			return self.whoPlayed(self.winningCard())
		else: return False
		
	def winningCard(self):
		"""
		Determine which card won the trick:
		* In a trump contract, the highest ranked trump card wins.
		* Otherwise, the highest ranked card in the lead suit wins. 
		"""
		if self.isComplete():
			topCard = self.cards[0]
			for card in self.cards[1:]:
				# Is the top card a trump?
				if topCard.suit == self.trumpSuit:
					# Am I a trump and am I higher ranked than top card?
					if card.suit == self.trumpSuit and card.rank > topCard.rank:
						topCard = card
				else:
					# Am I a trump?
					if card.suit == self.trumpSuit:
						topCard = card
					# Am I of the same suit as top card and am I higher ranked?
					elif card.suit == topCard.suit and card.rank > topCard.rank:
						topCard = card
			return topCard
		else: return False

class Play:
	"""
	"""

	def __init__(self, hands, declarer):
		self.hands = hands
		self.declarer = declarer
		self.tricks = []
	
	def isComplete(self):
		return len(self.tricks) == 13
	
	def addTrick(self, trick):
		if self.tricks:
			self.tricks.append 
	
	def lastTrick(self):
		if self.tricks:
			return self.tricks[-1]
		else:
			return False

	def declarerTrickCount(self):
		if self.isComplete():
			temp = ['n', 'e', 's', 'w']
			trickCount = 0
			for trick in self.tricks:
				trickCount += trick.whoWon() in [self.declarer, temp[(temp.index(self.declarer) + 2) % 4]]
			return trickCount
