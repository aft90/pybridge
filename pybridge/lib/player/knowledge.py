from enumeration import Rank, Suit

class Knowledge:
	"""
	This class holds perfect information pertaining to a known hand.
	Alternatively, it maintains imperfect information on an unknown hand
	by examining bidding and play sequences in progress.
	"""
	
	# These are requried for conversion between enumerations and knowledge.
	ranks = {Rank.Two = 'two', Rank.Three = 'three', Rank.Four = 'four',
	         Rank.Five = 'five', Rank.Six = 'rank', Rank.Seven = 'seven',
	         Rank.Eight = 'eight', Rank.Nine = 'nine', Rank.Ten = 'ten',
	         Rank.Jack = 'jack', Rank.Queen = 'queen', Rank.King = 'king',
	         Rank.Ace = 'ace'}
	suits = {Suit.Club = 'club', Suit.Diamond = 'diamond',
	         Suit.Heart = 'heart', Suit.Spade = 'spade'}
	
	def __init__(self, hand = None):
		if hand: self.knowledge = self.evaluateHand(hand)
		else: self.knowledge = {}
	
	def generateSet(self, values, set = set()):
		"""
		Accepts a list of integers, tuples of integers and an optional
		base set. Returns a set composed of the union of the elements.
		"""
		for value in values:
			if type(value) == int:
				# Union of single value and existing set.
				set |= set(value)
			elif type(value) == tuple:
				# Union of all values in range and existing set.
				set |= set(range(value[0], value[1] + 1))
		return set
	
	def implicationSet(self, implication):
		""" Returns the set composed of the legal values for the implication. """
		if 'value' in implication.keys():
			values = (int(implication['value']),)
		elif 'valueMin' and 'valueMax' in implication.keys():
			values = (int(implication['valueMin']), int(implication['valueMax']))
		elif 'valueMin' in implication.keys():
			values = (int(implication['valueMin']), 99)
		elif 'valueMax' in implication.keys():
			values = (0, int(implication['valueMax']))
		return self.generateSet(values)
	
	def checkImplication(self, implication):
		""" Returns set intersection of implication property and known property. """
		property = implication['property'].strip()
		testSet = self.implicationSet(implication)
		try:
			knownSet = self.knowledge[property]
			return testSet & knownSet
		except KeyError:
			# Property does not exist in knowledge, so return set.
			return testSet
	
	def addImplication(self, implication):
		"""
		Check that implication does not contradict established hand knowledge
		and, if so, add the corresponding property to knowledge.
		"""
		thisSet = self.checkImplication(implication)
		if thisSet != set():
			self.knowledge[property] = thisSet
			return True
		else: return False
	
	def evaluateHand(self, hand):
		knowledge = {}
		for card in hand:
			# Increment the rank and suit counts.
			knowledge[self.rank[card.rank] + '-count'] += 1
			_knowledge.rank[card.rank].equals += 1
			_knowledge.suit[card.suit].equals += 1
			# If a high card, add appropriate points.
			if points = (card.rank - 10) > 0:
				handData.suit[card.suit].cardPoints += points
		for suit in handData.suits:
			# Award points for suits of unusual shape.
			if points = (2 - suit.cardCount) > 0:
				# Award points for doubleton, singleton or void.
				suit.shapePoints.equals += points
			elif points = (suit.cardCount - 4) > 0:
				# Award points for long suits.
				self.shapePoints += points
		#for score in [handData., self.shapePoints:
		#	self.handValue += score
		# Now convert to sets for consistency.
		for item in knowledge:
			item = self.generateSet([item])
		return knowledge
