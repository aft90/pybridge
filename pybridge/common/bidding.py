# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2006 PyBridge Project.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from call import Call, Bid, Pass, Double, Redouble

from call import Level, Strain
from deck import Seat


class Bidding:
	"""A bidding session is a list of Call objects and the dealer."""

	# Enumeration of all available calls.
	BIDS     = [Bid(l, s) for l, s in zip(5*[l for l in Level], 7*[s for s in Strain])]
	DOUBLE   = Double()
	REDOUBLE = Redouble()
	PASS     = Pass()


	def __init__(self, dealer):
		assert(dealer in Seat)
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
		bid = self.currentCall(Bid)
		if bid and self.isComplete() and not self.isPassedOut():
			
			double, doubleBy = self.currentCall(Double), None
			if double:
				doubleBy = self.whoseCall(double)
			redouble, redoubleBy = self.currentCall(Redouble), None
			if redouble:
				redoubleBy = self.whoseCall(redouble)
			
			return {'bid' : bid,
			   'declarer' : self.whoseCall(bid),
			   'doubleBy' : doubleBy,
			 'redoubleBy' : redoubleBy, }
		
		else:
			return None


	def currentCall(self, type):
		"""Returns most recent current call of specified class type, or None."""
		assert(issubclass(type, Call))
		for call in self.calls[::-1]:
			if isinstance(call, type):
				return call
			elif isinstance(call, Bid):
				break
		return None


	def validCall(self, call):
		"""Check a given call for validity against the previous calls."""
		assert(isinstance(call, Call))
		return call in self.listAvailableCalls()


	def addCall(self, call):
		"""Add call to the calls list."""
		assert(isinstance(call, Call))
		assert(self.validCall(call))
		if self.validCall(call):  # In case asserts are disabled.
			self.calls.append(call)


	def listAvailableCalls(self):
		"""Returns a tuple of all calls available to current seat."""
		calls = []
		if not self.isComplete():
			currentBid = self.currentCall(Bid)

			# If bidding is not complete, a pass is always available.
			calls.append(self.PASS)

			# There must be an existing bid for a double or redouble.
			if currentBid:
				opposition = (self.whoseTurn(1), self.whoseTurn(3))
				partnership = (self.whoseTurn(0), self.whoseTurn(2))
				bidder = self.whoseCall(currentBid)
				# Check if double (on opposition's bid) is available.
				if not self.currentCall(Double) and bidder in opposition:
					calls.append(self.DOUBLE)
				# Check if redouble (on partnership's bid) is available.
				elif self.currentCall(Double) and bidder in partnership:
					calls.append(self.REDOUBLE)

			# Bids are available only if they are stronger than the current bid.
			calls += [bid for bid in self.BIDS if (not currentBid) or bid > currentBid]

		return calls


	def whoseTurn(self, offset=0):
		"""Returns the seat that is next to call."""
		assert(isinstance(offset, int))
		seat = Seat[(len(self.calls) + self.dealer.index + offset) % 4]
		return not(self.isComplete()) and seat


	def whoseCall(self, call):
		"""Returns the seat from which the call was made."""
		assert(isinstance(call, Call))
		assert(call in self.calls)
		return Seat[(self.calls.index(call) + self.dealer.index) % 4]

