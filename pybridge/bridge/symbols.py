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


from pybridge.enum import Enum


# Bid levels and strains (denominations).

Level = Enum('One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven')

Strain = Enum('Club', 'Diamond', 'Heart', 'Spade', 'NoTrump')


# Card ranks and suits.

Rank = Enum('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
            'Ten', 'Jack', 'Queen', 'King', 'Ace')

Suit = Enum('Club', 'Diamond', 'Heart', 'Spade')


# Player compass positions.

Direction = Enum('North', 'East', 'South', 'West')  # Clockwise order.
Player = Direction  # TODO: remove


# Vulnerability indicators.

Vulnerable = Enum('None', 'NorthSouth', 'EastWest', 'All')

