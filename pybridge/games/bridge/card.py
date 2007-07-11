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

from symbols import Rank, Suit


class Card(object, pb.Copyable, pb.RemoteCopy):
    """A card has a rank and a suit.
    
    @param rank: the rank of the card.
    @type rank: L{Rank}
    @param suit: the suit of the card.
    @type suit: L{Suit}
    """

    rank = property(lambda self: self.__rank)
    suit = property(lambda self: self.__suit)


    def __init__(self, rank, suit):
        if rank not in Rank:
            raise TypeError, "Expected Rank, got %s" % type(rank)
        if suit not in Suit:
            raise TypeError, "Expected Suit, got %s" % type(suit)

        self.__rank = rank
        self.__suit = suit


    def __eq__(self, other):
        """Two cards are equivalent if their ranks and suits match."""
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False


    def __cmp__(self, other):
        """Compare cards for hand sorting.
        
        Care must be taken when comparing cards of different suits.
        """
        if not isinstance(other, Card):
            raise TypeError, "Expected Card, got %s" % type(other)

        selfIndex = self.suit.index*13 + self.rank.index
        otherIndex = other.suit.index*13 + other.rank.index
        return cmp(selfIndex, otherIndex)


    def __hash__(self):
        return hash((self.rank, self.suit))


    def __repr__(self):
        return "Card(%s, %s)" % (self.rank, self.suit)


    def getStateToCopy(self):
        return self.rank, self.suit


    def setCopyableState(self, state):
        self.__rank, self.__suit = state


pb.setUnjellyableForClass(Card, Card)

