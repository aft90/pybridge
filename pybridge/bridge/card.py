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


class Card(pb.Copyable, pb.RemoteCopy):
    """A card has a rank and a suit."""


    def __init__(self, rank, suit):
        assert rank in Rank and suit in Suit
        self.rank = rank
        self.suit = suit


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


    def __str__(self):
        return "%s of %ss" % (self.rank, self.suit)


    def getStateToCopy(self):
        state = {}
        state['rank'] = self.rank.key
        state['suit'] = self.suit.key
        return state


    def setCopyableState(self, state):
        self.rank = getattr(Rank, state['rank'])
        self.suit = getattr(Suit, state['suit'])

