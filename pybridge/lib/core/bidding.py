class Call:
	"""
	A call is a bid, a pass or a (re)double.
	A bid is a denomination and a number of odd tricks.
	"""
	denomOrder = ['c', 'd', 'h', 's', 'n']
	denomNames = {'c' : 'Club', 'd' : 'Diamond', 'h' : 'Heart', 'n' : 'No Trump', 's' : 'Spade'}
	
	def __init__(self, call, bidOddTricks = False, bidDenom = False):
		"""
		Initialise a call.
		"""
		if call in ['bid', 'dbl', 'pass']:
			self.isBid = call == 'bid'
			self.isDouble = call == 'dbl'
			self.isPass = call == 'pass'
			if self.isBid:
				if bidOddTricks in range(1,8): self.bidOddTricks = bidOddTricks
				else: raise 'Bad specification of bid odd tricks'
				if bidDenom in self.denomOrder: self.bidDenom = bidDenom
				else: raise 'Bad specification of bid denomination'
		else: raise 'Bad specification of call type'
	
	def __cmp__(self, other):
		"""
		Compare two calls and return:
		1, if self call is greater than other call.
		0, if self call is same as other call.
		-1, if self call is less than other call.
		"""
		if self.isBid and other.isBid:
			# Compare bid calls by their trick count, then their trump count.
			selfStrength = self.bidOddTricks * 5 + self.denomOrder.index(self.bidDenom)
			otherStrength = other.bidOddTricks * 5 + self.denomOrder.index(other.bidDenom)
			return cmp(selfStrength, otherStrength)
		else:
			# Comparing non-bid call(s) returns true.
			return 1
	
	def __str__(self):
		if self.isBid: return str(self.bidOddTricks) + ' ' + self.denomNames[self.bidDenom]
		elif self.isDouble: return 'Double'
		elif self.isPass: return 'Pass'

class Bidding:
	"""
	A bidding session is a list of Call objects and the dealer.
	"""
	playerOrder = ['n', 'e', 's', 'w']

	def __init__(self, dealer):
		self.calls = []
		if dealer in self.playerOrder: self.dealer = dealer
		else: raise 'Bad specification of dealer'
	
	def isClosed(self):
		if len(self.calls) >= 4:
			return self.calls[-1].isPass and self.calls[-2].isPass and self.calls[-3].isPass
		else: return False
	
	def isOpen(self):
		return not self.isClosed()
	
	def addCall(self, call):
		"""
		If call is valid, add to the calls list.
		If at least 4 calls made and last 3 are passes, closes bidding.
		"""
		if self.validCall(call):
			self.calls.append(call)
			return True
		else: return False
	
	def validCall(self, call):
		"""
		A call is valid if all of the following:
			the bidding is open.
			the call is greater than the present contract.
			the call is not a double, or the call is a double and the contract is not redoubled.
		"""
		if self.isOpen():
			contract = self.contract()
			if contract:
				# Contract established.
				return (call > contract['bid'] and not (contract['isRedoubled'] and call.isDouble))
			else:
				# No contract established, so do not allow double.
				return not call.isDouble
		else: return False
	
	def contract(self):
		"""
		Iterate through the calls list backwards.
		If no contract established, return False.
		"""
		if self.calls:
			doubles = 0
			for call in self.calls[::-1]:
				if call.isDouble:
					doubles += 1
				elif call.isBid:
					return {'bid' : call,
					        'declarer' : self.whoMade(call),
					        'isDoubled' : doubles == 1,
					        'isRedoubled' : doubles == 2}
		return False
	
	def whoseTurn(self):
		if self.isOpen():
			return self.playerOrder[(len(self.calls) + self.playerOrder.index(self.dealer)) % 4]
		else: return False
	
	def whoMade(self, call):
		if call in self.calls:
			return self.playerOrder[(self.calls.index(call) + self.playerOrder.index(self.dealer)) % 4]
		else: return False
