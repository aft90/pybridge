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


from card import Card

# Enumerations.
from card import Suit
from deck import Seat


class Playing:
    """This class represents the playing of cards into tricks.

    This code is generalised, and could easily be adapted to support a
    variety of trick-taking card games.
    """

    def __init__(self, declarer, trumps):
        assert declarer in Seat
        assert trumps in Suit or trumps is None  # (None = No Trumps)
        self.trumps = trumps
        
        self.declarer = declarer
        self.dummy = Seat[(declarer.index + 2) % 4]
        self.lho = Seat[(declarer.index + 1) % 4]
        self.rho = Seat[(declarer.index + 3) % 4]
        
        # Each trick corresponds to a cross-section of lists.
        self.played = {}
        for seat in Seat:
            self.played[seat] = []
        self.winners = []  # Winning player of each trick.


    def isComplete(self):
        """Returns true for 13 complete tricks."""
        return len(self.winners) == 13


    def getTrick(self, index):
        """Returns a tuple specifying:
        
        - the leader seat.
        - a dict containing seat : card pairs, for each card in trick.
        """
        if index == 0:  # First trick.
            leader = self.lho  # Leader is declarer's left-hand opponent.
        else:  # Leader is winner of previous trick.
            leader = self.winners[index - 1]
        cards = {}
        for seat in Seat:
            # If length of list exceeds index value, player's card in trick.
            if len(self.played[seat]) > index:
                cards[seat] = self.played[seat][index]
        return leader, cards


    def getCurrentTrick(self):
        """Returns the getTrick() tuple of the current trick."""
        i = max([len(cards) for cards in self.played.values()])
        index = (i >= 1 and i-1) or 0
        return self.getTrick(index)


    def playCard(self, card):
        """Plays card to current trick. Assumes correct seat.
        
        Card validity should be checked with isValidPlay() beforehand.
        """
        assert isinstance(card, Card)
        # Skip the seat and hand checks here.
        assert self.isValidPlay(card, self.whoseTurn(), [card])
        
        self.played[self.whoseTurn()].append(card)
        
        # If trick is complete, determine winner.
        leader, cards = self.getCurrentTrick()
        if len(cards) == 4:
            winner = self.whoPlayed(self.winningCard(self.getCurrentTrick()))
            self.winners.append(winner)


    def isValidPlay(self, card, seat=None, hand=[]):
        """Card is playable if and only if:
        
        - Play session is not complete.
        - Seat is on turn to play.
        - Card exists in hand.
        - Card has not been previously played.
        
        In addition, if the current trick has an established lead, then
        card must follow lead suit OR hand must be void in lead suit.
        
        Specification of seat and hand  required for verification.
        """
        if self.isComplete():
            return False
        elif hand and card not in hand:
            return False  # Playing a card not in hand.
        elif seat and seat is not self.whoseTurn():
            return False  # Playing out of turn.
        elif self.whoPlayed(card):
            return False  # Card played previously.
        
        leader, cards = self.getCurrentTrick()
        # 0 if start of playing, 4 if complete trick.
        if len(cards) in (0, 4):
            return True  # Card will be first in next trick.
        
        else:  # Current trick has an established lead: check for revoke.
            leadcard = cards[leader]
            # Cards in hand that match suit of leadcard.
            followers = [c for c in hand if c.suit == leadcard.suit and not self.whoPlayed(c)]
            # Hand void in lead suit or card follows lead suit.
            return len(followers) == 0 or card in followers


    def whoPlayed(self, card):
        """If card is played, returns seat of player, otherwise False."""
        for seat, cards in self.played.items():
            if card in cards:
                return seat
        return False


    def whoseTurn(self):
        """Returns the seat that is on turn to play."""
        if not self.isComplete():
            trick = self.getCurrentTrick()
            leader, cards = trick
            if len(cards) == 4:  # If trick is complete, the trick winner's turn.
                return self.whoPlayed(self.winningCard(trick))
            else:
                return Seat[(leader.index + len(cards)) % 4]
        return False


    def winningCard(self, trick):
        """Determine which card wins the specified trick:
        
        - In a trump contract, the highest ranked trump card wins.
        - Otherwise, the highest ranked card of the lead suit wins.
        """
        leader, cards = trick
        if len(cards) == 4:  # Trick is complete.
            if self.trumps:  # Suit contract.
                trumpcards = [c for c in cards.values() if c.suit==self.trumps]
                if len(trumpcards) > 0:
                    return max(trumpcards)  # Highest ranked trump.
            # No Trump contract, or no trump cards played.
            followers = [c for c in cards.values() if c.suit==cards[leader].suit]
            return max(followers)  # Highest ranked card in lead suit.
        return False

