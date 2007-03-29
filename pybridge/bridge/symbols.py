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


"""
This module contains enumeration types used for the implementation of bridge.

The particular ordering of the values in each enumeration is assumed throughout
PyBridge, so it is vital that the order is not changed.
"""


from twisted.spread import pb

from pybridge.enum import Enum, EnumValue


class WeakEnumValue(EnumValue, pb.Copyable, pb.RemoteCopy):
    """A variant of EnumValue which may be copied across the network.
    
    Since the enumtype reference (an Enum object) cannot be maintained when this
    object is copied, it is discarded. An undesirable side-effect is that
    comparisons between WeakEnumValue objects with identical indexes and keys
    (but belonging to different Enum types) will result in True.
    """

    enumtype = property(lambda self: None)


    def __repr__(self):
        return "WeakEnumValue(%s, %s)" % (self.index, self.key)


    def __cmp__(self, other):
        try:
            assert self.key == other.key
            result = cmp(self.index, other.index)
        except (AssertionError, AttributeError):
            result = NotImplemented
        return result


    def getStateToCopy(self):
        return (self.index, self.key)


    def setCopyableState(self, (index, key)):
        # self = WeakEnumValue(None, index, key)
        self.__init__(None, index, key)


pb.setUnjellyableForClass(WeakEnumValue, WeakEnumValue)




# Bid levels and strains (denominations).

Level = Enum('One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven',
             value_type=WeakEnumValue)

Strain = Enum('Club', 'Diamond', 'Heart', 'Spade', 'NoTrump',
              value_type=WeakEnumValue)


# Card ranks and suits.

Rank = Enum('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
            'Ten', 'Jack', 'Queen', 'King', 'Ace', value_type=WeakEnumValue)

Suit = Enum('Club', 'Diamond', 'Heart', 'Spade', value_type=WeakEnumValue)


# Player compass positions, in clockwise order.

Direction = Enum('North', 'East', 'South', 'West', value_type=WeakEnumValue)


# Vulnerability indicators.

Vulnerable = Enum('None', 'NorthSouth', 'EastWest', 'All',
                  value_type=WeakEnumValue)

