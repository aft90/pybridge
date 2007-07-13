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
from symbols import Direction


class Trick(dict):
    """A trick is a set of cards, each played from the hand of a player."""


    def __init__(self, leader, trumpSuit):
        """
        @param leader: the position from which the lead card is played.
        @type declarer: Direction
        @param trumpSuit: the contract's trump suit: specify None for No Trumps.
        @type trumpSuit: Suit or None
        """
        self.leader = leader
        self.trumpSuit = trumpSuit

    winningCard = property(lambda self: self._getWinningCard())
    winner = property(lambda self: self.whoPlayed(self.winningCard))


    def isComplete(self):
        """The trick is complete when it contains a card from each position.
        
        @return: True if trick is complete, False otherwise.
        """
        return set(self.keys()) == set(Direction)  # A card from each position.


    def whoseTurn(self):
        """Returns the position from which the next card should be played.
        
        @return: the next position to play a card, or None.
        """
        if self.isComplete():
            return

        numCardsPlayed = len(self)
        return Direction[(self.leader.index + numCardsPlayed) % 4]


    def whoPlayed(self, playedcard):
        """Returns the position from which the specified card was played.
        
        @param playedcard: a card played in the trick.
        @return: the position of the card.
        """
        for position, card in self.iteritems():
            if card == playedcard:
                return position


    def _getWinningCard(self):
        """If the trick is complete, returns the winning card.
        
        - In a trump contract, the highest ranked trump card wins.
        - Otherwise, the highest ranked card following the lead suit wins.
        
        @return: the winning card, or None if trick is not complete.
        """
        if not self.isComplete():
            return

        if self.trumpSuit:  # Suit contract.
            # The highest ranked trump card wins.
            trumpcards = [c for c in self.values() if c.suit == self.trumpSuit]
            if trumpcards:
                return max(trumpcards)

        # No trump cards played, or No Trump contract.
        # The highest ranked card in the lead card's suit wins.
        leadsuit = self[self.leader].suit
        followers = [c for c in self.values() if c.suit == leadsuit]
        return max(followers)




class TrickPlay(list):
    """The trick-taking phase of a game of cards.
    
    This code is generalised, and could easily be adapted to support a
    variety of trick-taking card games.
    """


    def __init__(self, declarer, trumpSuit):
        """
        @param declarer: the declarer of the auction contract.
        @type declarer: Direction
        @param trumpSuit: the trump suit of the auction contract.
        @type trumpSuit: Suit or None
        """
        self.declarer = declarer
        self.trumpSuit = trumpSuit

    # Other positions, respective to declarer.
    dummy = property(lambda self: Direction[(self.declarer.index + 2) % 4])
    lho = property(lambda self: Direction[(self.declarer.index + 1) % 4])
    rho = property(lambda self: Direction[(self.declarer.index + 3) % 4])


    def isComplete(self):
        """Play is complete if there are 13 complete tricks.

        @return: True if play is complete, False otherwise.
        """
        return len([trick for trick in self if trick.isComplete()]) == 13


    def isValidCardPlay(self, card, deal):
        """Card is playable if all of the following are true:
        
        - The play session is not complete.
        - The position is on turn to play.
        - The card exists in hand.
        - The card has not been previously played in any trick.
        
        In addition, if the current trick has an established lead, then
        card must follow lead suit OR hand must be void in lead suit.
        
        Assumes that players do not attempt to play cards from other hands.

        @param card: the candidate card.
        @type card: Card
        @param deal: the original deal of hands.
        @type deal: {Direction: [Card]}
        @return: True if card is playable, False otherwise.
        """
        turn = self.whoseTurn()
        played = [trick[turn] for trick in self if trick.get(turn)]
        hand = set(deal[turn]) - set(played)  # Cards currently in hand.

        # Some sanity checks.
        if self.isComplete() or card not in hand:
            return False

        if len(self) == 0 or self[-1].isComplete():
            return True  # First card in the next (new) trick.

        # Current trick has an established lead: check for revoke.
        trick = self[-1]
        leadsuit = trick[trick.leader].suit
        followers = [c for c in hand if c.suit == leadsuit]
        # Hand void in lead suit, or card follows lead suit.
        return followers == [] or card in followers


    def playCard(self, card, position):
        """Plays card to current (or new) trick.
        
        Please note that card validity must be checked with isValidCardPlay()
        before calling this method!
        
        @param card: the card to be played.
        @type card: Card
        @param position: the position from which the card is to be played.
        @type position: Direction
        """
        assert not self.isComplete()
        assert self.whoseTurn() == position

        # If current trick is complete, instantiate a new trick.
        if len(self) == 0 or self[-1].isComplete():
            trick = Trick(leader=self.whoseTurn(), trumpSuit=self.trumpSuit)
            self.append(trick)
        else:
            trick = self[-1]
            assert trick.get(position) is None

        trick[position] = card


    def whoseTurn(self):
        """Returns the position from which the next card should be played.
        
        @return: the next position to play a card, or None.
        """
        if self.isComplete():
            return

        try:
            currentTrick = self[-1]  # Raises IndexError if no tricks.
        except IndexError:
            return self.lho  # Declarer's LHO leads the first trick.

        if currentTrick.isComplete():
            return currentTrick.winner  # The winner leads the next trick.
        else:
            return currentTrick.whoseTurn()


    def wonTricks(self):
        """Returns, for each position a list of tricks won by that position.
        
        @return: a dict containing, for each position, the list of won tricks.
        @rtype: {Direction: [Trick]}
        """
        won = dict([(pos, []) for pos in Direction])
        for trick in self:
            if trick.isComplete():  # Trick is complete <=> trick has winner.
                won[trick.winner].append(trick)
        return won


    def wonTrickCount(self):
        """Returns the number of tricks won by declarer/dummy and by defenders.
        
        @return: a 2-tuple containing the declarer and defender trick counts.
        @rtype: (int, int)
        """
        tricks = self.wonTricks()
        declarerWon = len(tricks[self.declarer]) + len(tricks[self.dummy])
        defenceWon = len(tricks[self.lho]) + len(tricks[self.rho])
        return (declarerWon, defenceWon)

