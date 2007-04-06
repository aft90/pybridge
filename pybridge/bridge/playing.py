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


from card import Card
from symbols import Direction, Suit


class Playing(object):
    """This class models the trick-taking phase of a game of bridge.
    
    This code is generalised, and could easily be adapted to support a
    variety of trick-taking card games.
    """

    # TODO: tricks, leader, winner properties?


    def __init__(self, declarer, trumpSuit):
        """
        @param declarer: the declarer from the auction.
        @type declarer: Direction
        @param trumpSuit: the trump suit from the auction.
        @type trumpSuit: Suit or None
        """
        if declarer not in Direction:
            raise TypeError, "Expected Direction, got %s" % type(declarer)
        if trumpSuit not in Suit and trumpSuit is not None:  # None => No Trumps
            raise TypeError, "Expected Suit, got %s" % type(trumpSuit)
        
        self.trumps = trumpSuit
        self.declarer = declarer
        self.dummy = Direction[(declarer.index + 2) % 4]
        self.lho = Direction[(declarer.index + 1) % 4]
        self.rho = Direction[(declarer.index + 3) % 4]
        
        # Each trick corresponds to a cross-section of lists.
        self.played = {}
        for position in Direction:
            self.played[position] = []
        self.winners = []  # Winning player of each trick.


    def isComplete(self):
        """Playing is complete if there are 13 complete tricks.
        
        @return: True if playing is complete, False if not.
        """
        return len(self.winners) == 13


    def getTrick(self, index):
        """A trick is a set of cards, one from each player's hand.
        The leader plays the first card, the others play in clockwise order.
        
        @param: trick index, in range 0 to 12.
        @return: a (leader, cards) trick tuple.
        """
        assert 0 <= index < 13
        
        if index == 0:  # First trick.
            leader = self.lho  # Leader is declarer's left-hand opponent.
        else:  # Leader is winner of previous trick.
            leader = self.winners[index - 1]
        cards = {}
        for position in Direction:
            # If length of list exceeds index value, player's card in trick.
            if len(self.played[position]) > index:
                cards[position] = self.played[position][index]
        return leader, cards


    def getCurrentTrick(self):
        """Returns the getTrick() tuple of the current trick.
        
        @return: a (leader, cards) trick tuple.
        """
        # Index of current trick is length of longest played list minus 1.
        index = max(0, max([len(cards) for cards in self.played.values()]) - 1)
        return self.getTrick(index)


    def getTrickCount(self):
        """Returns the number of tricks won by declarer/dummy and by defenders.
        
        @return: the declarer trick count, the defender trick count.
        @rtype: tuple
        """
        declarerCount, defenderCount = 0, 0

        for i in range(len(self.winners)):
            trick = self.getTrick(i)
            winner = self.whoPlayed(self.winningCard(trick))
            if winner in (self.declarer, self.dummy):
                declarerCount += 1
            else:  # Trick won by defenders.
                defenderCount += 1

        return declarerCount, defenderCount


    def playCard(self, card, player=None, hand=[]):
        """Plays card to current trick.
        Card validity should be checked with isValidPlay() beforehand.
        
        @param card: the Card object to be played from player's hand.
        @param player: the player of card, or None.
        @param hand: the hand of player, or [].
        """
        assert isinstance(card, Card)
        player = player or self.whoseTurn()
        hand = hand or [card]  # Skip hand check.
        
        valid = self.isValidPlay(card, player, hand)
        assert valid
        if valid:  # In case assert is disabled.
            self.played[player].append(card)
        
        # If trick is complete, determine winner.
        trick = self.getCurrentTrick()
        leader, cards = trick
        if len(cards) == 4:
            winner = self.whoPlayed(self.winningCard(trick))
            self.winners.append(winner)


    def isValidPlay(self, card, player=None, hand=[]):
        """Card is playable if and only if:
        
        - Play session is not complete.
        - Direction is on turn to play.
        - Card exists in hand.
        - Card has not been previously played.
        
        In addition, if the current trick has an established lead, then
        card must follow lead suit OR hand must be void in lead suit.
        
        Specification of player and hand are required for verification.
        """
        assert isinstance(card, Card)
        
        if self.isComplete():
            return False
        elif hand and card not in hand:
            return False  # Playing a card not in hand.
        elif player and player != self.whoseTurn():
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
            followers = [c for c in hand if c.suit == leadcard.suit 
                                         and not self.whoPlayed(c)]
            # Hand void in lead suit or card follows lead suit.
            return len(followers) == 0 or card in followers


    def whoPlayed(self, card):
        """Returns the player who played the specified card.
        
        @param card: a Card.
        @return: the player who played card.
        """
        assert isinstance(card, Card)
        for player, cards in self.played.items():
            if card in cards:
                return player
        return False


    def whoseTurn(self):
        """If playing is not complete, returns the player who is next to play.
        
        @return: the player next to play.
        """
        if not self.isComplete():
            trick = self.getCurrentTrick()
            leader, cards = trick
            if len(cards) == 4:  # If trick is complete, trick winner's turn.
                return self.whoPlayed(self.winningCard(trick))
            else:  # Otherwise, turn is next (clockwise) player in trick.
                return Direction[(leader.index + len(cards)) % 4]
        return False


    def winningCard(self, trick):
        """Determine which card wins the specified trick:
        
        - In a trump contract, the highest ranked trump card wins.
        - Otherwise, the highest ranked card of the lead suit wins.

        @param: a complete (leader, cards) trick tuple.
        @return: the Card object which wins the trick.
        """
        leader, cards = trick
        if len(cards) == 4:  # Trick is complete.
            if self.trumps:  # Suit contract.
                trumpcards = [c for c in cards.values() if c.suit==self.trumps]
                if len(trumpcards) > 0:
                    return max(trumpcards)  # Highest ranked trump.
            # No Trump contract, or no trump cards played.
            followers = [c for c in cards.values()
                         if c.suit==cards[leader].suit]
            return max(followers)  # Highest ranked card in lead suit.
        return False

