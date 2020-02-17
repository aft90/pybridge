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

from .deal import Deal
from .result import DuplicateResult, RubberResult
from .symbols import Direction, Vulnerable


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


    @classmethod
    def first(cls, deal=None):
        """Builds an initial board.
        
        @deal: if provided, the deal to be wrapped by board.
               Otherwise, a randomly-generated deal is wrapped.
        """
        board = cls()
        board['deal'] = deal or Deal.fromRandom()
        board['num'] = 1
        board['time'] = tuple(time.localtime())

        # Convention for duplicate bridge.
        board['dealer'] = Direction.North
        board['vuln'] = Vulnerable.None

        return board


    def next(self, deal=None):
        """Builds and returns a successor board to this board.
        
        The dealer and vulnerability of the successor board are determined from
        the board number, according to the rotation scheme for duplicate bridge.
        
        @param deal: if provided, the deal to be wrapped by next board.
                     Otherwise, a randomly-generated deal is wrapped.
        """
        board = Board(self.copy())  # copy() returns a dict.
        board['deal'] = deal or Deal.fromRandom()
        board['num'] = board.get('num', 0) + 1
        board['time'] = tuple(time.localtime())

        # Dealer rotates clockwise.
        board['dealer'] = Direction[(board['dealer'].index + 1) % 4]

        # Map from duplicate board index range 1..16 to vulnerability.
        # See http://www.d21acbl.com/References/Laws/node5.html#law2
        i = (board['num'] - 1) % 16
        board['vuln'] = Vulnerable[(i%4 + i/4)%4]

        return board

