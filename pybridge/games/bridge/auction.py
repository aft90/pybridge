# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2007 PyBridge Project.
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
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from twisted.spread import pb

from .call import Bid, Pass, Double, Redouble
from .symbols import Direction


class Contract(object, pb.Copyable, pb.RemoteCopy):
    """Represents the result of an auction."""


    def __init__(self, auction):
        """
        @param auction: a completed, but not passed out, auction.
        @type auction: Auction
        """
        assert auction.isComplete() and not auction.isPassedOut()

        # The contract is the last (and highest) bid.
        self.bid = auction.currentBid

        # The declarer is the first partner to bid the contract denomination.
        caller = auction.whoCalled(self.bid)
        partnership = (caller, Direction[(caller.index + 2) % 4])
        # Determine which partner is declarer.
        for call in auction:
            if isinstance(call, Bid) and call.strain == self.bid.strain:
                bidder = auction.whoCalled(call)
                if bidder in partnership:
                    self.declarer = bidder
                    break

        self.doubleBy, self.redoubleBy = None, None
        if auction.currentDouble:
            # The opponent who doubled the contract bid.
            self.doubleBy = auction.whoCalled(auction.currentDouble)
            if auction.currentRedouble:
                # The partner who redoubled an opponent's double.
                self.redoubleBy = auction.whoCalled(auction.currentRedouble)


    def getStateToCopy(self):
        return self.bid, self.declarer, self.doubleBy, self.redoubleBy


    def setCopyableState(self, state):
        self.bid, self.declarer, self.doubleBy, self.redoubleBy = state


pb.setUnjellyableForClass(Contract, Contract)




class Auction(list):
    """The auction (bidding phase) of a game of bridge."""


    def __init__(self, dealer):
        """
        @param dealer: who distributes the cards and makes the first call.
        @type dealer: Direction
        """
        self.dealer = dealer
        self.contract = None

    currentBid = property(lambda self: self._getCurrentCall(Bid))
    currentDouble = property(lambda self: self._getCurrentCall(Double))
    currentRedouble = property(lambda self: self._getCurrentCall(Redouble))


    def isComplete(self):
        """Auction is complete if all players have called (ie. 4 or more calls)
        and the last 3 calls are Pass calls.
        
        @return: True if bidding is complete, False if not.
        @rtype: bool
        """
        passes = len([c for c in self[-3:] if isinstance(c, Pass)])
        return len(self) >= 4 and passes == 3


    def isPassedOut(self):
        """Auction is passed out if each player has passed on their first turn.
        In this case, the bidding is complete, but no contract is established.
        
        @return: True if bidding is passed out, False if not.
        @rtype: bool
        """
        passes = len([call for call in self if isinstance(call, Pass)])
        return len(self) == 4 and passes == 4


    def makeCall(self, call):
        """Appends call from position to the calls list.
        
        Please note that call validity should be checked with isValidCall()
        before calling this method!

        @param call: a candidate call.
        """
        assert call not in self  # Calls must be distinct.
        assert self.isValidCall(call)

        self.append(call)
        if self.isComplete() and not self.isPassedOut():
            self.contract = Contract(self)


    def isValidCall(self, call, position=None):
        """Check that call can be made, according to the rules of bidding.

        @param call: the candidate call.
        @param position: if specified, the position from which the call is made.
        @return: True if call is available, False if not.
        """
        # The bidding must not be complete.
        if self.isComplete():
            return False
 
        # Position's turn to play.
        if position and position != self.whoseTurn():
            return False

        # A pass is always available.
        if isinstance(call, Pass):
            return True

        # A bid must be greater than the current bid.
        if isinstance(call, Bid):
            return not self.currentBid or call > self.currentBid

        # Doubles and redoubles only when a bid has been made.
        if self.currentBid:
            bidder = self.whoCalled(self.currentBid)

            # A double must be made on the current bid from opponents,
            # with has not been already doubled by partnership.
            if isinstance(call, Double):
                opposition = (Direction[(self.whoseTurn().index + 1) % 4],
                              Direction[(self.whoseTurn().index + 3) % 4])
                return bidder in opposition and not self.currentDouble

            # A redouble must be made on the current bid from partnership,
            # which has been doubled by an opponent.
            elif isinstance(call, Redouble):
                partnership = (self.whoseTurn(),
                               Direction[(self.whoseTurn().index + 2) % 4])
                return bidder in partnership and self.currentDouble \
                                         and not self.currentRedouble

        return False  # Otherwise unavailable.


    def whoCalled(self, call):
        """Returns the position from which the specified call was made.
        
        @param call: a call made in the auction.
        @return: the position of the player who made call, or None.
        """
        if call in self:
            return Direction[(self.dealer.index + self.index(call)) % 4]
        return None  # Call not made by any player.


    def whoseTurn(self):
        """Returns the position from which the next call should be made.
        
        @return: the next position to make a call, or None.
        """
        if self.isComplete():
            return
        return Direction[(self.dealer.index + len(self)) % 4]


    def _getCurrentCall(self, callclass):
        """Returns most recent current call of specified class, or None.
        
        @param callclass: call class, in (Bid, Pass, Double, Redouble).
        @return: most recent call matching type, or None.
        """
        assert callclass in (Bid, Pass, Double, Redouble)

        for call in reversed(self):
            if isinstance(call, callclass):
                return call
            elif isinstance(call, Bid):
                break  # Bids cancel all preceding calls.
        return None

