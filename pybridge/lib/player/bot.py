#from biddingsystem import BiddingSystem
from knowledge import HandKnowledge
from core.bidding import Call
from core.enumeration import Rank, Seat, Suit

class BiddingBot:
	"""This class chooses the call that the bot should make.
	
	It does this by using rules established in the bidding system, knowledge
	of the bot's hand and imperfect knowledge of the hands of other players.
	
	Bidding is divided into three parts:
	- evaluation of candidate calls
	- selection of call
	- execution of returned call (by player class)
	"""
	
	# Clockwise.
	_seatOrder = [Seat.North, Seat.East, Seat.South, Seat.West]

	ourContexts = theirContexts = ['openings']

	def __init__(self, mySeat, hand, bidding, ourSystem, theirSystem):
		self.bidding = bidding
		self.ourSystem = ourSystem.definitions
		self.theirSystem = theirSystem.definitions
		# Determine the seat correspondence.
		self.players = {}
		self.players['me'], self.players['lho'], self.players['partner'], self.players['rho'] = [self._seatOrder[(self._seatOrder.index(seat) + self._seatOrder.index(mySeat)) % 4] for seat in self._seatOrder]
		# Instantiate the knowledge objects.
		self.knowledge = dict.fromkeys(self.players.keys(), HandKnowledge())
		self.knowledge['me'].evaluate(hand)

	def buildSet(self, values, xset=set()):
		for value in values:
			if type(value) == int:
				# Union of single value and existing set.
				xset |= set(value)
			elif type(value) == tuple:
				# Union of all values in range and existing set.
				xset |= set(range(value[0], value[1] + 1))
		return xset

	def buildProperties(self, implications):
		"""Generates a property from an implication."""
		properties = dict.fromkeys(self.players.keys(), {})
		for implication in implications:
			# Build set composed of values.
			value = implication.get('value', None)
			valueMin = implication.get('value-min', 0)
			valueMax = implication.get('value-max', 99)  # eek
			set = self.buildSet([value, (valueMin, valueMax)])
			# Determine where to place set in properties.
			#player = self.players[implication['player']]
			player = implication['player'] # wheep!
			name = implication['property']
			# We must take union of an existing property.
			if properties[player].has_key(property):
				properties[player][name] |= set
			else:
				properties[player][name] = set
		return properties

	def ruleIsApplicable(self, rule):
		"""Returns true if no implication conflicts with hand knowledge."""
		properties = self.buildProperties(rule['implies'])
		# Now "intersect" properties and knowledge.
		for player, property in properties.items():
			print property
			for name, valueSet in property.items():
				# Check that property does not contradict knowledge.
				if self.knowledge[player][name]:
					if not (valueSet & self.knowledge[player][name]):
						return False
		return True

	def generateCalls(self, rule):
		"""Generates a list of Call objects from a given rule."""
		calls = []
		for call in rule['own-calls']:
			type = call['type']
			level = call.get('level', None)
			denomination = call.get('denomination', None)
			calls.append(Call(type, level, denomination))
		return calls

	def getCallRule(self, call, contexts, system):
		"""Returns the rule identifier for a given call, from a list of given contexts."""
		for context in contexts:
			for key, rule in system[context].items():
				calls = self.generateCalls(self, rule)
				if call in calls: return key
		return False

	def selectCall(self, calls):
		"""Chooses the "best" call to make."""
		callCount = len(calls)
		if callCount == 0:
			call = Call('pass')
		elif callCount == 1:
			call = calls[0]
		else:
			call = calls[1]  # This is not very clever.
			# Monte Carlo should appear here soon.
		return call
	
	def execute(self):
		"""Serves as a "front-end" for bot."""
		if self.players['me'] == self.bidding.whoseTurn():
			# Determine implications for partner's and oppositions' calls.
			for call in self.bidding.calls[-3:]:
				if self.bidding.whoMade(call) in \
				[self.players['me'], self.players['partner']]:
					system = self.ourSystem
					contexts = self.ourContexts
				else:
					system = self.theirSystem
					contexts = self.theirContexts
				rule = self.getCallRule(call, contexts, system)
				properties = self.buildProperties(rule)[player]
				for name, set in properties:
					# Take intersection of knowledge.
					self.knowledge[player][name] &= set
				# Now determine new contexts.
				contexts = rule['scope'] # Will this work?
			# Now determine which calls we can make.
			calls = []
			for context in self.ourContexts:
				rules = self.ourSystem[context]
				for rule in rules.values():
					if self.ruleIsApplicable(rule):
						calls.extend(self.generateCalls(rule))
			return self.selectCall(calls)
		else: return False

class PlayingBot:

	def __init__(self):
		pass
