from enumeration import Denomination, Seat

class Call:
	"""
	A call is a bid, a pass or a (re)double.
	A bid is a level and a denomination.
	"""
	
	denominationStrength = {Denomination.Club : 0, Denomination.Diamond : 1,
	                        Denomination.Heart : 2, Denomination.Spade : 3,
	                        Denomination.NoTrump : 4}	
	
	def __init__(self, callType, bidLevel = False, bidDenomination = False):
		""" Initialise a call. """
		if callType in ['bid', 'double', 'pass']:
			self.isBid = callType == 'bid'
			self.isDouble = callType == 'double'
			self.isPass = callType == 'pass'
			if self.isBid:
				if bidLevel in range(1,8):
					self.bidLevel = bidLevel
				else: raise 'Bad specification of bid level.'
				if bidDenomination in Denomination.Denominations:
					self.bidDenomination = bidDenomination
				else: raise 'Bad specification of bid denomination.'
		else: raise 'Bad specification of call type.'
	
	def __cmp__(self, other):
		"""
		Compare two calls and return:
			1, if self call is greater than other call.
			0, if self call is same as other call.
			-1, if self call is less than other call.
		"""

		if self.isBid and other.isBid:
			# Compare bid calls by their trick count, then their denomination strength.
			selfStrength = self.bidLevel * 5 + denominationStrength[self.bidDenomination]
			otherStrength = other.bidLevel * 5 + denominationStrength[other.bidDenomination]
			return cmp(selfStrength, otherStrength)
		else:
			# Comparing non-bid call returns true.
			return 1
	
	#def __str__(self):
	#	if self.isBid:
	#		return str(self.bidLevel) + ' ' + self.denomNames[self.bidDenom]
	#	elif self.isDouble: return 'Double'
	#	elif self.isPass: return 'Pass'

class Bidding:
	""" A bidding session is a list of Call objects and the dealer. """
	
	seatOrder = [Seat.North, Seat.East, Seat.South, Seat.West]
	
	def __init__(self, dealer):
		self.calls = []
		self.dealer = dealer
	
	def isPassedOut(self):
		""" If at least 4 calls made and last 3 are passes, closes bidding. """
		if len(self.calls) >= 4:
			return self.calls[-1].isPass and self.calls[-2].isPass and self.calls[-3].isPass
		else: return False
	
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
		""" If call is valid, add to the calls list. """
		if self.validCall(call):
			self.calls.append(call)
			return True
		else: return False
	
	def validCall(self, call):
		""" Check a call for validity against the previous calls. """
		# The bidding must not be passed out.
		if not self.isPassedOut():
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
		if not self.isPassedOut():
			return self.seatOrder[(len(self.calls) + self.seatOrder.index(self.dealer)) % 4]
		else: return False
	
	def whoseCall(self, call):
		if call in self.calls:
			return self.seatOrder[(self.calls.index(call) + self.seatOrder.index(self.dealer)) % 4]
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
