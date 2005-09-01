from enumeration import CallType, Denomination, Seat


class Call:
	"""A call represents a bid, a pass or a (re)double."""


	def __init__(self, type, bidLevel=False, bidDenom=False):
		self.callType = type
		if type not in CallType.CallTypes:
			raise "Invalid specification of call."
		elif type == CallType.Bid:
			if bidLevel in range(1,8) and bidDenom in Denomination.Denominations:
				self.bidLevel = bidLevel
				self.bidDenom = bidDenom
			else:
				raise "Invalid specification of bid."


	def __cmp__(self, other):
		"""Compares two bids.
		
		Returns:
		- 1, if self call is greater than other call.
		- 0, if self call is same as other call.
		- -1, if self call is less than other call.
		"""
		if self.callType == other.callType == CallType.Bid:
			# Compare bids by their level and then their denomination.
			selfIndex = (self.bidLevel * 5) + Denomination.Denominations.index(self.bidDenom)
			otherIndex = (other.bidLevel * 5) + Denomination.Denominations.index(other.bidDenom)
			return cmp(selfIndex, otherIndex)
		else:
			return 1  # Comparing non-bid call types returns true.


	def __str__(self):
		if self.callType is CallType.Bid:
			return "%s %s" % (self.bidLevel, self.bidDenom)
		else:
			return self.callType
		


class Bidding:
	"""A bidding session is a list of Call objects and the dealer."""


	def __init__(self, dealer):
		self.calls = []
		self.dealer = dealer


	def isComplete(self):
		"""Bidding is complete if:
		
		- at least 4 calls made.
		- last 3 calls are passes.
		"""
		if len(self.calls) >= 4:
			return len([call for call in self.calls[-3:] if call.callType==CallType.Pass]) == 3
		else:
			return False


	def isPassedOut(self):
		"""Bidding is passed out if each player has passed on their first turn. This implies no contract."""
		if len(self.calls) == 4:
			return len([call for call in self.calls if call.callType==CallType.Pass]) == 4
		else:
			return False


	def contract(self):
		"""A contract is the final state of the bidding."""
		if self.isComplete() and self.currentBid():
			return {'bidDenom'    : self.currentBid().bidDenom,
			        'bidLevel'    : self.currentBid().bidLevel,
			        'declarer'    : self.whoseCall(self.currentBid()),
			        'doubleLevel' : self.currentDoubleLevel() }
		else:  # No bids, no contract.
			return None


	def currentBid(self):
		"""Returns most recent bid, or False if no bids made."""
		bids = [call for call in self.calls if call.callType==CallType.Bid]
		if len(bids) > 0:
			return bids[-1]
		else:
			return False


	def currentDoubleLevel(self):
		"""Returns:

		- 0, if current bid is not doubled.
		- 1, if current bid is doubled.
		- 2, if current bid is redoubled.
		"""
		doubles = 0
		for call in self.calls[::-1]:
			doubles += (call.callType == CallType.Double)
			if call.callType is CallType.Bid:
				break
		return doubles


	def addCall(self, call):
		"""Add call to the calls list."""
		if self.validCall(call):
			self.calls.append(call)


	def validCall(self, call):
		"""Check a given call for validity against the previous calls."""

		# The bidding must not be passed out.
		if self.isComplete():
			return False

		elif call.callType == CallType.Bid:
			# A bid must be greater than the current bid.
			return (not self.currentBid()) or call > self.currentBid()

		elif call.callType == CallType.Double:
			# If opposition's bid, must be single double.
			# If partnership's bid, must be redouble.
			bidder = self.whoseCall(self.currentBid())
			if bidder in (self.whoseTurn(), self.whoseTurn(2)):  # partnership
				return self.currentDoubleLevel() == 1  # opponent double
			elif bidder in (self.whoseTurn(1), self.whoseTurn(3)):  # opposition
				return self.currentDoubleLevel() == 0  # no double
			else:  # No bid, so double is invalid.
				return False

		else:  # call.callType == CallType.Pass
			# Bidding is not complete, so pass is valid.
			return True


	def whoseTurn(self, offset=0):
		"""Returns the seat that is next to call."""
		if self.isComplete():
			return False
		else:
			return Seat.Seats[(len(self.calls) + Seat.Seats.index(self.dealer) + offset) % 4]


	def whoseCall(self, call):
		"""Returns the seat from which the call was made."""
		if call in self.calls:
			return Seat.Seats[(self.calls.index(call) + Seat.Seats.index(self.dealer)) % 4]
		else:
			return False
