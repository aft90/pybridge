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
		if self.isBid:
			return str(self.bidOddTricks) + ' ' + self.denomNames[self.bidDenom]
		elif self.isDouble: return 'Double'
		elif self.isPass: return 'Pass'

class Bidding:
	"""
	A bidding session is a list of Call objects and the dealer.
	"""
	playerOrder = ['n', 'e', 's', 'w']

	def __init__(self, dealer):
		self.calls = []
		self.contract = False
		self.dealer = dealer
	
	def isPassedOut(self):
		if len(self.calls) >= 4:
			return self.calls[-1].isPass and self.calls[-2].isPass and self.calls[-3].isPass
		else: return False
	
	def isOpen(self):
		return not self.isPassedOut()
	
	def currentBid(self):
		if self.calls:
			for pastCall in self.calls:
				if pastCall.isBid: return pastCall
		return False
	
	def currentDoubleLevel(self):
		"""
		Returns:
			0, if current bid is not doubled.
			1, if current bid is doubled.
			2, if current bid is redoubled.
		"""
		doubleCount = 0
		if self.calls:
			for pastCall in self.calls:
				if pastCall.isDouble:
					doubleCount += 1
				elif pastCall.isBid:
					return doubleCount
		return doubleCount
	
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
		Check a call for validity against the previous calls.
		"""
		# The bidding must not be passed out.
		if self.isOpen():
			if call.isBid:
				# A bid must be greater than the current bid.
				return call > self.currentBid()
			elif call.isDouble:
				# A double must be on an existing bid.
				# The existing bid must not be already redoubled.
				return self.currentBid() and self.currentDoubleLevel() < 2
			elif call.isPass:
				# A pass is always valid.
				return True
		else: return False
		
	def whoseTurn(self):
		if self.isOpen():
			return self.playerOrder[(len(self.calls) + self.playerOrder.index(self.dealer)) % 4]
		else: return False
	
	def whoseCall(self, call):
		if call in self.calls:
			return self.playerOrder[(self.calls.index(call) + self.playerOrder.index(self.dealer)) % 4]
		else: return False

class Contract:
	"""
	A contract is an overlay for a bidding object.
	It only returns content pertaining to a contract.
	"""
	
	def __init__(self, bidding):
		self.bidding = bidding
	
	def isMade(self):
		return self.bidding.isPassedOut()
	
	def current(self):
		return {'bid' : self.bidding.currentBid(),
		        'declarer' : self.bidding.whoseCall(self.bidding.currentBid()),
		        'isDoubled' : self.bidding.currentDoubleLevel() == 1,
		        'isRedoubled' : self.bidding.currentDoubleLevel() == 2}
