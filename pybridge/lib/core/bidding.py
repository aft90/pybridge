from enumeration import CallType, Denomination, Level, Seat


class Call:
	"""A call represents a bid, a pass, a double or a redouble."""


	# TODO: decide if call types would be better implemented by inheritance.

	def __init__(self, type, bidLevel=False, bidDenom=False):
		"""
		pre:
			type in CallType.CallTypes
			(type == CallType.Bid) => (bidLevel in Level.Levels and bidDenom in Denomination.Denominations)
		"""
		self.callType = type
		self.bidLevel = bidLevel
		self.bidDenom = bidDenom


	def __cmp__(self, other):
		"""Compares two bids.
		
		Returns:
		- 1, if self call is greater than other call.
		- 0, if self call is same as other call.
		- -1, if self call is less than other call.

		pre:
			isinstance(other, Call)
		"""
		if self.callType == other.callType == CallType.Bid:
			# Compare bids by their level and then their denomination.
			selfIndex = (self.bidLevel * 5) + Denomination.Denominations.index(self.bidDenom)
			otherIndex = (other.bidLevel * 5) + Denomination.Denominations.index(other.bidDenom)
			return cmp(selfIndex, otherIndex)
		else:
			return 1  # Comparing non-bid call types returns true.


	def __eq__(self, other):
		if self.callType == other.callType == CallType.Bid:
			return self.bidLevel == other.bidLevel and self.bidDenom == other.bidDenom
		return self.callType == other.callType


	def __str__(self):
		if self.callType is CallType.Bid:
			return "%s %s" % (self.bidLevel, self.bidDenom)
		else:
			return self.callType


class Bidding:
	"""A bidding session is a list of Call objects and the dealer."""

	# Enumeration of all available calls.
	BIDS     = [Call(CallType.Bid, l, d) for l, d in zip(5*Level.Levels, 7*Denomination.Denominations)]
	DOUBLE   = Call(CallType.Double)
	REDOUBLE = Call(CallType.Redouble)
	PASS     = Call(CallType.Pass)


	def __init__(self, dealer):
		"""
		pre:
			dealer in Seat.Seats
		"""
		self.calls  = []
		self.dealer = dealer


	def isComplete(self):
		"""Bidding is complete if:
		
		- at least 4 calls made.
		- last 3 calls are passes.
		"""
		passes = len([call for call in self.calls[-3:] if call==self.PASS])
		return len(self.calls) >= 4 and passes == 3


	def isPassedOut(self):
		"""Bidding is passed out if each player has passed on their first turn.
		
		This is a special case of isComplete; it implies no contract has been established.
		"""
		passes = len([call for call in self.calls if call==self.PASS])
		return len(self.calls) == 4 and passes == 4


	def contract(self):
		"""A contract is the final state of the bidding."""
		if self.isComplete() and self.currentBid():
			return {
				'bidDenom'    : self.currentBid().bidDenom,
				'bidLevel'    : self.currentBid().bidLevel,
				'declarer'    : self.whoseCall(self.currentBid()),
				'doubleLevel' : self.currentDoubleLevel(),
			}
		else:  # No bids, no contract.
			return None


	def currentBid(self):
		"""Returns most recent bid, or False if no bids made."""
		bids = [call for call in self.calls if call in self.BIDS]
		return len(bids)>0 and bids[-1]


	def currentDoubleLevel(self):
		"""Returns:

		- 0, if current bid is not doubled.
		- 1, if current bid is doubled.
		- 2, if current bid is redoubled.
		"""
		for call in self.calls[::-1]:
			if call in self.BIDS:
				break
			elif call == self.DOUBLE:
				return 1
			elif call == self.REDOUBLE:
				return 2
		return 0


	def validCall(self, call):
		"""Check a given call for validity against the previous calls.
		
		pre:
			isinstance(call, Call)
		"""
		return call in self.listAvailableCalls()


	def addCall(self, call):
		"""Add call to the calls list.
		
		pre:
			isinstance(call, Call)
			self.validCall(call)
		"""
		if self.validCall(call):
			self.calls.append(call)


	def listAvailableCalls(self):
		"""Returns a tuple of all calls available to current seat."""
		calls = []
		if not self.isComplete():
			currentBid = self.currentBid()

			# If bidding is not complete, a pass is always available.
			calls.append(self.PASS)

			# There must be an existing bid for a double or redouble.
			if currentBid:
				opposition = (self.whoseTurn(1), self.whoseTurn(3))
				partnership = (self.whoseTurn(0), self.whoseTurn(2))
				bidder = self.whoseCall(currentBid)
				# Check if double (on opposition's bid) is available.
				if self.currentDoubleLevel() == 0 and bidder in opposition:
					calls.append(self.DOUBLE)
				# Check if redouble (on partnership's bid) is available.
				elif self.currentDoubleLevel() == 1 and bidder in partnership:
					calls.append(self.REDOUBLE)

			# Bids are available only if they are stronger than the current bid.
			calls += [bid for bid in self.BIDS if (not currentBid) or bid > currentBid]

		return calls


	def whoseTurn(self, offset=0):
		"""Returns the seat that is next to call."""
		seat = Seat.Seats[(len(self.calls) + Seat.Seats.index(self.dealer) + offset) % 4]
		return not(self.isComplete()) and seat


	def whoseCall(self, call):
		"""Returns the seat from which the call was made.
		
		pre:
			isinstance(call, Call)
			call in self.calls
		"""
		return Seat.Seats[(self.calls.index(call) + Seat.Seats.index(self.dealer)) % 4]
