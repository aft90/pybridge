# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2006 PyBridge Project.
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

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import random  # To shuffle a deck.

from card import Card, Rank, Suit

from pybridge.enum import Enum

Seat = Enum('North', 'East', 'South', 'West')  # Clockwise.


class Deck:
    """A Deck consists of 52 Card objects."""

    def __init__(self):
        self.cards = [Card(r, s) for r in Rank for s in Suit]


    def dealOrdered(self, combination):
        """Returns a deal, ordered by combination."""
        pass  # Not implemented yet.


    def dealRandom(self):
        """Returns a deal, from a shuffled deck."""
        random.shuffle(self.cards)
        hands = {}
        for seat in Seat:
            hands[seat] = []
        for index, card in enumerate(self.cards):
            hands[Seat[index % len(Seat)]].append(card)
        for hand in hands.values():
            hand.sort()
        return hands

