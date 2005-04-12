from core.enumeration import Rank, Suit

class HandKnowledge:
	"""Class to represent knowledge of a hand.
	
	This class holds perfect information pertaining to a known hand.
	Alternatively, it maintains imperfect information on an unknown hand
	by examining bidding and play sequences in progress.
	"""

	_categories = ['hand', 'rank', 'suit'] + Rank.Ranks + Suit.Suits
	_properties = ['count', 'points-card', 'points-shape', 'points-all']

	# I'm not too sure about these valuations. What do you think?
	_cardPoints = {Rank.Jack : 1, Rank.Queen : 2, Rank.King : 3, Rank.Ace : 4}
	_shapePoints = {0 : 3, 1 : 2, 2 : 1, 5 : 1, 6 : 2, 7 : 3, 8 : 4, 9 : 5,
	                10 : 6, 11 : 7, 12 : 8, 13 : 9}

	_knowledge = {}

	def __init__(self, hand=None):
		if hand: self.evaluate(hand)

	def __getitem__(self, key):
		category, property = key.split('-', 1)
		if category in self._categories and property in self._properties:
			try:
				return self._knowledge[key]
			except KeyError:
				return None
		else:
			raise IndexError, "key does not match any known property"

	def __setitem__(self, key, value):
		if type(value) == int:
			# This is shorthand to specify a single value set.
			self._knowledge[key] = set(value)
		elif type(value) == set:
			if self[key] != None:
				intersection = self[key] & value
				if intersection != set():
					self._knowledge[key] = intersection
				else:
					raise ValueError, "values are incompatible"
			else:
				self._knowledge[key] = value
		else:
			raise TypeError, "value must be of type Set"

	def evaluate(self, hand):
		values = {}
		for card in hand.cards:
			# Increment the rank and suit counts.
			values[card.rank + '-count'] = values.get(card.rank + 'count', 0) + 1
			values[card.suit + '-count'] = values.get(card.suit + 'count', 0) + 1
			# If a high card, add appropriate points.
			points = self._cardPoints.get(card.rank, 0)
			values[card.suit + '-points-card'] = values.get(card.suit + '-points-card', 0) + points
		for suit in Suit.Suits:
			# Award points for suits of unusual shape.
			points = self._shapePoints.get(self[suit + '-count'], 0)
			values[suit + '-points-shape'] = values.get(suit + '-points-shape', 0) + points
		# Now convert to knowledge set.
		for key, value in values.items():
			self[key] = set([value])
