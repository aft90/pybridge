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


from copy import copy
from operator import mul
import random

from card import Card
from symbols import Direction, Rank, Suit


# See http://mail.python.org/pipermail/edu-sig/2001-May/001288.html for details.
comb = lambda n, k: reduce(mul, range(n, n-k, -1)) / reduce(mul, range(1, k+1))


class Deal(dict):
    """Represents a deal of hands as a dict containing lists of cards.
    
    Operations to encode/decode deals into a variety of formats are provided,
    including "impossible bridge book" index values and PBN strings.
    
    Definitions:
    - A hand is a collection of 13 cards from the deck.
    - A deal is a distribution of all 52 cards to four hands.
    
    There are exactly 52! / (13!)**4 (comb(52,13) * comb(39,13) * comb(26,13))
    distinct deals of 13 cards to 4 positions from a standard 52-card deck.
    """

    # Required order: Ace of Spades, King of Spades, ..., Two of Clubs.
    __cards = [Card(r, s) for s in reversed(Suit) for r in reversed(Rank)]

    __Nmax = comb(52, 13)
    __Emax = comb(39, 13)
    __Smax = comb(26, 13)
    __D = __Nmax * __Emax * __Smax


    def __init__(self, mapping):
        super(Deal, self).__init__(mapping)
        for hand in self.values():
            hand.sort()


    @classmethod
    def fromRandom(cls):
        """Generates a random deal of hands from a 'shuffled' deck.

        @return: an instance of Deal.
        """
        # This is more efficient than calling fromIndex() with a random number.
        deck = copy(cls.__cards)
        random.shuffle(deck)
        hands = dict((pos, sorted(deck[13*i : 13*(i+1)]))
                     for i, pos in enumerate(Direction))
        return cls(hands)


    @classmethod
    def fromIndex(cls, num):
        """Generates the deal which corresponds to the specified "page number".
        
        This implements the "impossible bridge book" decoding algorithm by
        Thomas Andrews, see http://bridge.thomasoandrews.com/impossible/.
        
        @param num: integer in range 1..D.
        @return: a Deal object containing the corresponding deal.
        """
        assert isinstance(num, (int, long)), "index must be an integer"
        assert 1 <= num <= cls.__D, "index not in range %s..%s" % (1, cls.__D)

        cardSeq = copy(cls.__cards)  # Make a copy for modification.
        hands = dict((pos, []) for pos in Direction)
        num -= 1  # Decrement page number to fit within range 0..D-1.

        # Split index into hand indexes.
        indexes = {Direction.North : (num / cls.__Smax) / cls.__Emax,
                   Direction.East  : (num / cls.__Smax) % cls.__Emax,
                   Direction.South : (num % cls.__Smax) }

        for position in (Direction.North, Direction.East, Direction.South):
            for k in range(13, 0, -1):

                # Find the largest n such that comb(n, k) <= indexes[position].
                n = k-1  # n < k implies comb(n, k) = 0
                # comb(n+1, k) =
                #   n-k == -1 => comb(n, k) * (n+1)
                #   otherwise => (comb(n, k) * (n+1)) / (n+1 - k)
                while comb(n+1, k) <= indexes[position]:
                    n += 1

                # Remove card index from indices, add card to hand.
                indexes[position] -= comb(n, k)
                card = cardSeq[n]
                hands[position].append(card)
                cardSeq.remove(card)

        hands[Direction.West] = cardSeq  # West has the remaining cards.

        return cls(hands)


    def toIndex(self):
        """Computes the "page number" which corresponds to this deal.
        
        This implements the "impossible bridge book" encoding algorithm by
        Thomas Andrews, see http://bridge.thomasoandrews.com/impossible/.
        
        @return: integer in range 1..D
        """
        cardSeq = copy(self.__cards)  # Make a copy for modification.
        indexes = {}

        # For each hand, compute indexes of cards in cardSeq.
        for position in (Direction.North, Direction.East, Direction.South):
            indexes[position] = 0
            self[position].sort(reverse=False)
            # It is desirable to remove cards from cardSeq when adding their
            # indexes, instead of doing so in an extra step.
            # Removing cards backwards preserves the indexes of later cards.
            for i, card in enumerate(self[position]):
                indexes[position] += comb(cardSeq.index(card), 13-i)
                cardSeq.remove(card)

        # Deal index = (Nindex * Emax * Smax) + (Eindex * Smax) + Sindex
        indexes[Direction.North] *= self.__Emax * self.__Smax
        indexes[Direction.East]  *= self.__Smax

        num = sum(indexes.values()) + 1  # Increment to fit within range 1..D.
        return long(num)


    __pbnDirection = dict(zip('NESW', Direction))
    __pbnRank = dict(zip('23456789TJQKA', Rank))


    @classmethod
    def fromString(cls, dealstr):
        """Generates the deal which corresponds to the given PBN deal string.
        
        As per the PBN specification, the given deal string should conform to
        the format "<first>:<1st_hand> <2nd_hand> <3rd_hand> <4th_hand>".
        
        @param dealstr: a PBN deal string.
        @return: a Deal object containing the corresponding deal.
        """
        # Reconstruct deal.
        first, hands = dealstr.split(":")
        firstindex = cls.__pbnDirection[first.strip()].index
        order = Direction[firstindex:] + Direction[:firstindex]

        deal = dict((pos, []) for pos in Direction)

        for position, hand in zip(order, hands.strip().split(' ')):
            for suit, suitcards in zip(reversed(Suit), hand.split('.')):
                for rank in suitcards:
                    card = Card(cls.__pbnRank[rank], suit)
                    deal[position].append(card)

        return cls(deal)


    def toString(self):
        """Computes the PBN deal string which corresponds to this deal.
        
        @return: a PBN deal string.
        """
        raise NotImplementedError

