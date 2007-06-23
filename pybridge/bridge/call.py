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

    def __hash__(self):
        return hash(self.__class__.__name__)


    def __repr__(self):
        return "%s()" % self.__class__.__name__


class Bid(Call):
    """A Bid represents a statement of a level and a strain.
    
    @param level: the level of the bid.
    @type level: L{Level}
    @param strain: the strain (denomination) of the bid.
    @type strain: L{Strain}
    """

    level = property(lambda self: self.__level)
    strain = property(lambda self: self.__strain)


    def __init__(self, level, strain):
        if level not in Level:
            raise TypeError, "Expected Level, got %s" % type(level)
        if strain not in Strain:
            raise TypeError, "Expected Strain, got %s" % type(strain)

        self.__level = level
        self.__strain = strain


    def __cmp__(self, other):
        if not issubclass(other.__class__, Call):
            raise TypeError, "Expected Call, got %s" % type(other)

        if isinstance(other, Bid):  # Compare two bids.
            selfIndex = self.level.index*len(Strain) + self.strain.index
            otherIndex = other.level.index*len(Strain) + other.strain.index
            return cmp(selfIndex, otherIndex)
        else:  # Comparing non-bid calls returns true.
            return 1


    def __hash__(self):
        return hash((self.level, self.strain))


    def __repr__(self):
        return "Bid(%s, %s)" % (self.level, self.strain)


    def getStateToCopy(self):
        return self.level, self.strain


    def setCopyableState(self, state):
        self.__level, self.__strain = state


pb.setUnjellyableForClass(Bid, Bid)


class Pass(Call):
    """A Pass represents an abstention from the bidding."""


pb.setUnjellyableForClass(Pass, Pass)


class Double(Call):
    """A Double over an opponent's current bid."""


pb.setUnjellyableForClass(Double, Double)


class Redouble(Call):
    """A Redouble over an opponent's double of partnership's current bid."""


pb.setUnjellyableForClass(Redouble, Redouble)

