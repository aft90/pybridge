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

from symbols import Level, Strain


class Call(pb.Copyable, pb.RemoteCopy):
    """Abstract class, inherited by Bid, Pass, Double and Redouble."""


class Bid(Call):
    """A Bid represents a statement of a level and a strain."""

    def __init__(self, level, strain):
        assert level in Level
        assert strain in Strain
        
        self.level = level
        self.strain = strain


    def __cmp__(self, other):
        if not issubclass(other.__class__, Call):
            raise TypeError, "Expected Call, got %s" % type(other)
        
        if isinstance(other, Bid):  # Compare two bids.
            selfIndex = self.level.index*len(Strain) + self.strain.index
            otherIndex = other.level.index*len(Strain) + other.strain.index
            return cmp(selfIndex, otherIndex)
        else:  # Comparing non-bid calls returns true.
            return 1


    def __str__(self):
        return "%s %s" % (self.level, self.strain)


    def getStateToCopy(self):
        state = {}
        state['level'] = self.level.key
        state['strain'] = self.strain.key
        return state


    def setCopyableState(self, state):
        self.level = getattr(Level, state['level'])
        self.strain = getattr(Strain, state['strain'])


class Pass(Call):
    """A Pass represents an abstention from the bidding."""

    def __str__(self):
        return "Pass"


class Double(Call):
    """A Double over an opponent's current bid."""

    def __str__(self):
        return "Double"


class Redouble(Call):
    """A Redouble over an opponent's double of partnership's current bid."""

    def __str__(self):
        return "Redouble"

