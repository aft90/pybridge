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

from enum import Enum

# Bid levels and strains (denominations).

class Level(pb.Copyable, pb.RemoteCopy, Enum):
    One = 0
    Two = 1
    Three = 2
    Four = 3
    Five = 4
    Six = 5
    Seven = 6

pb.setUnjellyableForClass(Level, Level)

class Strain(pb.Copyable, pb.RemoteCopy, Enum):
    Club = 0
    Diamond = 1
    Heart = 2
    Spade = 3
    NoTrump = 4

pb.setUnjellyableForClass(Strain, Strain)


# Card ranks and suits.


class Rank(pb.Copyable, pb.RemoteCopy, Enum):
    Two = 0
    Three = 1
    Four = 2
    Five = 3
    Six = 4
    Seven = 5
    Eight = 6
    Nine = 7
    Ten = 8
    Jack = 9
    Queen = 10
    King = 11
    Ace = 12

pb.setUnjellyableForClass(Rank, Rank)

class Suit(pb.Copyable, pb.RemoteCopy, Enum):
    Club = 0
    Diamond = 1
    Heart = 2
    Spade = 3

pb.setUnjellyableForClass(Suit, Suit)


# Player compass positions, in clockwise order.

class Direction(pb.Copyable, pb.RemoteCopy, Enum):
    North = 0
    East = 1
    South = 2
    West = 3

pb.setUnjellyableForClass(Direction, Direction)

# Vulnerability indicators.

class Vulnerable(pb.Copyable, pb.RemoteCopy, Enum):
    Nil = 0
    NorthSouth = 1
    EastWest = 2
    All = 3

pb.setUnjellyableForClass(Vulnerable, Vulnerable)
