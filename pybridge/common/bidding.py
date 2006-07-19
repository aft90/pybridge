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


	def __init__(self, dealer):
		assert(dealer in Seat)
		self.calls  = []
		self.dealer = dealer


	def isComplete(self):
		"""Bidding is complete if:
		
		- at least 4 calls made.
		- last 3 calls are passes.
		"""
		passes = len([call for call in self.calls[-3:] if isinstance(call, Pass)])
		return len(self.calls) >= 4 and passes == 3


	def isPassedOut(self):
		"""Bidding is passed out if each player has passed on their first turn.
		
		This is a special case of isComplete; it implies no contract has been established.
		"""
		passes = len([call for call in self.calls if isinstance(call, Pass)])
		return len(self.calls) == 4 and passes == 4


	def contract(self):
		"""A contract is the final state of the bidding."""
		bid = self.currentCall(Bid)
		if bid and self.isComplete() and not self.isPassedOut():
			double = self.currentCall(Double)
			redouble = self.currentCall(Redouble)
			# Declarer is first player in partnership to bid the contract strain.
			partnership = (self.whoseCall(bid), Seat[(self.whoseCall(bid).index + 2) % 4])
			for call in self.calls:
				if isinstance(call, Bid) and self.whoseCall(call) in partnership and call.strain == bid.strain:
					declarerBid = call
					break
			
			return {'bid'        : bid,
			        'declarer'   : self.whoseCall(declarerBid),
			        'doubleBy'   : double and self.whoseCall(double),
			        'redoubleBy' : redouble and self.whoseCall(redouble) }
		
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
		
		# The bidding must not be passed out.
		if self.isComplete():
			return False
		
		# Bidding is not complete; a pass is always available.
		elif isinstance(call, Pass):
			return True
		
		currentBid = self.currentCall(Bid)
		
		# A bid must be greater than the current bid.
		if isinstance(call, Bid):
			return not currentBid or call > currentBid
		
		# Doubles and redoubles only when a bid has been made.
		if currentBid:
			bidder = self.whoseCall(currentBid)
			
			# A double must be made on the current bid from opponents,
			# with has not been already doubled by partnership.
			if isinstance(call, Double):
				opposition = (self.whoseTurn(1), self.whoseTurn(3))
				return not self.currentCall(Double) and bidder in opposition
			
			# A redouble must be made on the current bid from partnership,
			# which has been doubled by an opponent.
			elif isinstance(call, Redouble):
				partnership = (self.whoseTurn(0), self.whoseTurn(2))
				return self.currentCall(Double) and bidder in partnership
		
		return False  # Otherwise unavailable.


	def addCall(self, call):
		"""Add call to the calls list."""
		assert(isinstance(call, Call))
		assert(self.validCall(call))
		if self.validCall(call):  # In case asserts are disabled.
			self.calls.append(call)


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

