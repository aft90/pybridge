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


from call import Call, Bid, Pass, Double, Redouble
from symbols import Level, Player, Strain


class Bidding:
    """This class models the bidding (auction) phase of a game of bridge.
    
    A bidding session is a list of Call objects and the dealer.
    """


    def __init__(self, dealer):
        assert dealer in Player
        self.calls  = []
        self.dealer = dealer


    def isComplete(self):
        """Bidding is complete if 4 or more calls have been made,
        and the last 3 calls are Pass calls.

        @return: True if bidding is complete, False if not.
        """
        passes = len([c for c in self.calls[-3:] if isinstance(c, Pass)])
        return len(self.calls) >= 4 and passes == 3


    def isPassedOut(self):
        """Bidding is passed out if each player has called Pass on their
        first turn. This implies no contract has been established.
        Note that this is a special case of isComplete().

        @return: True if bidding is passed out, False if not.
        """
        passes = len([call for call in self.calls if isinstance(call, Pass)])
        return len(self.calls) == 4 and passes == 4


    def getContract(self):
        """When the bidding is complete, the contract is the last and highest
        bid, which may be doubled or redoubled.

        Hence, the contract represents the "final state" of the bidding.
        
        @return['bid']: the last and highest bid.
        @return['declarer']: the partner who first called the contract strain.
        @return['doubleBy']: the opponent who doubled the contract, or None.
        @return['redoubleBy']: the partner who redoubled an opponent's double
                               on the contract, or None.
        """
        bid = self.getCurrentCall(Bid)
        if bid and self.isComplete() and not self.isPassedOut():
            double = self.getCurrentCall(Double)
            redouble = self.getCurrentCall(Redouble)
            # Determine declarer.
            partnership = (self.whoCalled(bid), \
                           Player[(self.whoCalled(bid).index + 2) % 4])
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


    def getCurrentCall(self, type):
        """Returns most recent current call of specified type, or None.
        
        @param type: call type, in (Bid, Pass, Double, Redouble).
        @return: most recent call matching type, or None.
        """
        assert issubclass(type, Call)
        for call in self.calls[::-1]:
            if isinstance(call, type):
                return call
            elif isinstance(call, Bid):
                break
        return None


    def makeCall(self, call, player=None):
        """Appends call from player to the calls list.
        
        @param call: the Call object representing player's call.
        @param player: the player making call, or None.
        """
        assert isinstance(call, Call)
        valid = self.isValidCall(call, player)
        assert valid
        if valid:  # In case assert is disabled.
            self.calls.append(call)


    def isValidCall(self, call, player=None):
        """Check that specified call is available to player, with respect to
        current state of bidding. If specified, player's turn will be checked.
        
        @param call: the Call object to be tested for validity.
        @param player: the player attempting to call, or None.
        @return: True if call is available, False if not.
        """
        assert isinstance(call, Call)
        assert player in Player or player is None
        
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
                opposition = (Player[(self.whoseTurn().index + 1) % 4],
                              Player[(self.whoseTurn().index + 3) % 4])
                return bidder in opposition and not self.getCurrentCall(Double)
            
            # A redouble must be made on the current bid from partnership,
            # which has been doubled by an opponent.
            elif isinstance(call, Redouble):
                partnership = (self.whoseTurn(),
                               Player[(self.whoseTurn().index + 2) % 4])
                return bidder in partnership and self.getCurrentCall(Double) \
                       and not self.getCurrentCall(Redouble)
        
        return False  # Otherwise unavailable.


    def whoCalled(self, call):
        """Returns the player who made the specified call.
        
        @param call: a Call.
        @return: the player who made call, or False.
        """
        assert isinstance(call, Call)
        if call in self.calls:
            return Player[(self.calls.index(call) + self.dealer.index) % 4]
        return False  # Call not made by any player.


    def whoseTurn(self):
        """If bidding is not complete, returns the player who is next to call.
        
        @return: the player next to call.
        """
        player = Player[(len(self.calls) + self.dealer.index) % 4]
        return not self.isComplete() and player

