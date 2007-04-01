# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2007 PyBridge Project.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not write to the Free Software
# Foundation Inc. 51 Franklin Street Fifth Floor Boston MA 02110-1301 USA.


import random
import time
from deck import Deck
from symbols import Direction, Vulnerable


class Board(dict):
    """An encapsulation of board information.
    
    @keyword deal: the cards in each hand.
    @type deal: Deal
    @keyword dealer: the position of the dealer.
    @type dealer: Direction
    @keyword event: the name of the event where the board was played.
    @type event: str
    @keyword num: the board number.
    @type num: int
    @keyword players: a mapping from positions to player names.
    @type players: dict
    @keyword site: the location (of the event) where the board was played.
    @type site: str
    @keyword time: the date/time when the board was generated.
    @type time: time.struct_time
    @keyword vuln: the board vulnerability.
    @type vuln: Vulnerable
    """


    def nextDeal(self, result=None):
        """Generates and stores a random deal for the board.
        
        If result of a previous game is provided, the dealer and vulnerability
        are rotated according to the rules of bridge.
        
        @param result:
        @type result:
        """
        deck = Deck()
        self['deal'] = deck.randomDeal()

        self['num'] = self.get('num', 0) + 1
        self['time'] = tuple(time.localtime())

        if self.get('dealer'):  # Rotate dealer.
            self['dealer'] = Direction[(self['dealer'].index + 1) % 4]
        else:  # Select any player as the dealer.
            self['dealer'] = random.choice(Direction)

        if result:
            self['vuln'] = Vulnerable.All  # TODO
        else:
            self['vuln'] = Vulnerable.None  # The default value.
