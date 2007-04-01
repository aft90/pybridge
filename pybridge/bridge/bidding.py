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


from pybridge.network.error import GameError

from call import Bid, Pass, Double, Redouble
from symbols import Direction, Level, Strain


class Bidding(object):
    """This class models the bidding (auction) phase of a game of bridge.
    
    A bidding session is a list of Call objects and the dealer.
    """


    def __init__(self, dealer):
        if dealer not in Direction:
            raise TypeError, "Expected Direction, got %s" % type(dealer)
        self.calls  = []
        self.dealer = dealer


    def isComplete(self):
        """Bidding is complete if 4 or more calls have been made,
        and the last 3 calls are Pass calls.

        @return: True if bidding is complete, False if not.
        @rtype: bool
        """
        passes = len([c for c in self.calls[-3:] if isinstance(c, Pass)])
        return len(self.calls) >= 4 and passes == 3


    def isPassedOut(self):
        """Bidding is passed out if each player has passed on their first turn.
        In this case, the bidding is complete, but no contract is established.
        
        @return: True if bidding is passed out, False if not.
        @rtype: bool
        """
        passes = len([call for call in self.calls if isinstance(call, Pass)])
        return len(self.calls) == 4 and passes == 4


    def getContract(self):
        """When the bidding is complete, the contract is the last and highest
        bid, which may be doubled or redoubled.
        
        Hence, the contract represents the "final state" of the bidding.
        
        @return: a dict containing the keywords:
        @keyword bid: the last and highest bid.
        @keyword declarer: the partner who first bid the contract strain.
        @keyword doubleBy: the opponent who doubled the contract, or None.
        @keyword redoubleBy: the partner who redoubled an opponent's double
                             on the contract, or None.
        """
        if self.isComplete() and not self.isPassedOut():
            bid = self.getCurrentCall(Bid)
            double = self.getCurrentCall(Double)
            redouble = self.getCurrentCall(Redouble)
            # Determine partnership.
            caller = self.whoCalled(bid)
            partnership = (caller, Direction[(caller.index + 2) % 4])
            # Determine declarer.
            for call in self.calls:
                if isinstance(call, Bid) and call.strain == bid.strain \
                and self.whoCalled(call) in partnership:
                    declarerBid = call
                    break
            
            return {'bid'        : bid,
                    'declarer'   : self.whoCalled(declarerBid),
                    'doubleBy'   : double and self.whoCalled(double),
                    'redoubleBy' : redouble and self.whoCalled(redouble) }
        return None  # Bidding passed out or not complete, no contract.


    def getCurrentCall(self, calltype):
        """Returns most recent current call of specified type, or None.
        
        @param calltype: call type, in (Bid, Pass, Double, Redouble).
        @return: most recent call matching type, or None.
        """
        if calltype not in (Bid, Pass, Double, Redouble):
            raise GameError, "Expected call type, got %s" % type(calltype)

        for call in self.calls[::-1]:
            if isinstance(call, calltype):
                return call
            elif isinstance(call, Bid):
                break
        return None


    def makeCall(self, call, player=None):
        """Appends call from player to the calls list.
        
        @param call: the Call object representing player's call.
        @param player: the player making call, or None.
        """
        if not isinstance(call, (Bid, Pass, Double, Redouble)):
            raise GameError, "Expected call type, got %s" % type(call)
        if not self.isValidCall(call, player):
            raise GameError, "Invalid call"

        self.calls.append(call)


    def isValidCall(self, call, player=None):
        """Check that specified call is available to player, with respect to
        current state of bidding. If specified, player's turn will be checked.
        
        @param call: the Call object to be tested for validity.
        @param player: the player attempting to call, or None.
        @return: True if call is available, False if not.
        """
        if not isinstance(call, (Bid, Pass, Double, Redouble)):
            raise GameError, "Expected call type, got %s" % type(call)
        assert player in Direction or player is None
        
        # The bidding must not be complete.
        if self.isComplete():
            return False
        
        # It must be player's turn to call.
        if player and player != self.whoseTurn():
            return False
        
        # Bidding is not complete; a pass is always available.
        elif isinstance(call, Pass):
            return True
        
        currentBid = self.getCurrentCall(Bid)
        
        # A bid must be greater than the current bid.
        if isinstance(call, Bid):
            return not currentBid or call > currentBid
        
        # Doubles and redoubles only when a bid has been made.
        if currentBid:
            bidder = self.whoCalled(currentBid)
            
            # A double must be made on the current bid from opponents,
            # with has not been already doubled by partnership.
            if isinstance(call, Double):
                opposition = (Direction[(self.whoseTurn().index + 1) % 4],
                              Direction[(self.whoseTurn().index + 3) % 4])
                return bidder in opposition and not self.getCurrentCall(Double)
            
            # A redouble must be made on the current bid from partnership,
            # which has been doubled by an opponent.
            elif isinstance(call, Redouble):
                partnership = (self.whoseTurn(),
                               Direction[(self.whoseTurn().index + 2) % 4])
                return bidder in partnership and self.getCurrentCall(Double) \
                       and not self.getCurrentCall(Redouble)
        
        return False  # Otherwise unavailable.


    def whoCalled(self, call):
        """Returns the player who made the specified call.
        
        @param call: a Call.
        @return: the player who made call, or False.
        """
        if not isinstance(call, (Bid, Pass, Double, Redouble)):
            raise GameError, "Expected call type, got %s" % type(call)

        if call in self.calls:
            return Direction[(self.calls.index(call) + self.dealer.index) % 4]
        return False  # Call not made by any player.


    def whoseTurn(self):
        """Returns position of player who is next to make a call.
        
        @return: the current turn.
        @rtype: Direction
        """
        if self.isComplete():
            raise GameError, "Bidding complete"
        return Direction[(len(self.calls) + self.dealer.index) % 4]

