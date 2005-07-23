from enumeration import CallType, Denomination, Seat


class Call:
	"""A call represents a bid, a pass or a (re)double."""


	denomStrength = {Denomination.Club : 0, Denomination.Diamond : 1,
	                 Denomination.Heart : 2, Denomination.Spade : 3,
	                 Denomination.NoTrump : 4}	


	def __init__(self, callType, bidLevel = False, bidDenom = False):
		if callType in CallType.CallTypes:
			self.callType = type
			if callType == CallType.Bid:
				if bidLevel in range(1,8) and bidDenom in Denomination.Denominations:
					self.bidLevel = bidLevel
					self.bidDenomination = bidDenomination
				else:
					raise "Invalid specification of bid."
		else:
			raise "Invalid specification of call."


	def __cmp__(self, other):
		"""Compares two bids.
		
		Returns:
		- 1, if self call is greater than other call.
		- 0, if self call is same as other call.
		- -1, if self call is less than other call.
		"""
		if self.callType == other.callType == CallType.Bid:
			# Compare bids by their level and then their denomination.
			selfIndex = (5 * self.bidLevel) + self.denomStrength[self.bidDenomination]
			otherIndex = (5 * other.bidLevel) + self.denomStrength[other.bidDenomination]
			return cmp(selfIndex, otherIndex)
		else:
			return 1  # Comparing non-bid call types returns true.


class Bidding:
	""" A bidding session is a list of Call objects and the dealer. """


	seatOrder = [Seat.North, Seat.East, Seat.South, Seat.West]


	def __init__(self, dealer):
		self.calls = []
		self.dealer = dealer


	def isPassedOut(self):
		""" If at least 4 calls made and last 3 are passes, closes bidding. """
		if len(self.calls) >= 4:
			return self.calls[-1].callType == self.calls[-2].callType == self.calls[-3].callType == CallType.Pass
		else: return False


	def currentBid(self):
		"""Returns most recent call of Bid type, or False if no bids made."""
		for pastCall in self.calls[::-1]:
			if pastCall.callType == CallType.Bid:
				return pastCall
		return False  # No bids made.


	def currentDoubleLevel(self):
		"""Returns:
		- 0, if current bid is not doubled.
		- 1, if current bid is doubled.
		- 2, if current bid is redoubled.
		"""
		doubleCount = 0
		if self.calls:
			for pastCall in self.calls:
				if pastCall.isDouble:
					doubleCount += 1
				elif pastCall.isBid:
					return doubleCount
		return doubleCount


	def validCall(self, call):
		""" Check a call for validity against the previous calls. """
		# The bidding must not be passed out.
		if not self.isPassedOut():
			if call.callType == CallType.Bid:
				# A bid must be greater than the current bid.
				return call > self.currentBid() 
			elif call.callType == CallType.Double:
				# A double must be on an existing bid.
				# The existing bid must not be already redoubled.
				return self.currentBid() and self.currentDoubleLevel() < 2
			else:  # Pass.
				return True  # A pass is always valid.
		else: return False


	def addCall(self, call):
		""" If call is valid, add to the calls list. """
		if self.validCall(call):
			self.calls.append(call)
			return True
		else:
			return False


	def whoseTurn(self):
		if not self.isPassedOut():
			return self.seatOrder[(len(self.calls) + self.seatOrder.index(self.dealer)) % 4]
		else: return False


	def whoseCall(self, call):
		if call in self.calls:
			return self.seatOrder[(self.calls.index(call) + self.seatOrder.index(self.dealer)) % 4]
		else: return False


	def contract(self):
		"""A contract is an overlay for a bidding object."""
		if self.isPassedOut:
			return {'bid' : self.currentBid(),
			        'declarer' : self.whoseCall(self.currentBid()),
			        'isDoubled' : self.currentDoubleLevel() == 1,
			        'isRedoubled' : self.currentDoubleLevel() == 2}
		else:
			return False
