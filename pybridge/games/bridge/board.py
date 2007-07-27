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

from deal import Deal
from result import DuplicateResult, RubberResult
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


    @classmethod
    def first(cls, deal=None):
        """Build an initial board.
        
        @deal: if provided, the deal to be wrapped by board.
               Otherwise, a randomly-generated deal is wrapped.
        """
        board = cls()
        board['deal'] = deal or Deal.fromRandom()
        board['num'] = 1
        board['time'] = tuple(time.localtime())

        board['dealer'] = Direction.North  # Arbitary.
        board['vuln'] = Vulnerable.None

        return board


    def next(self, results, deal=None):
        """Given the results for this board (and all previous boards),
        builds the next board.
        
        The dealer and vulnerability of the next board are calculated
        from the results provided.
        
        @param result: a list of all previous results, ordered from earliest
                       to most recent, ie. this board's result is last in list.
        @param deal: if provided, the deal to be wrapped by next board.
                     Otherwise, a randomly-generated deal is wrapped.
        """
        boardresult = results[-1]
        assert boardresult.board == self

        board = Board(self.copy())  # copy() returns a dict.
        board['deal'] = deal or Deal.fromRandom()
        board['num'] = board.get('num', 0) + 1
        board['time'] = tuple(time.localtime())

        # Dealer rotates clockwise.
        board['dealer'] = Direction[(board['dealer'].index + 1) % 4]

        if isinstance(boardresult, DuplicateResult):
            # See http://www.d21acbl.com/References/Laws/node5.html#law2
            i = (board['num'] - 1) % 16
            # Map from duplicate board index range 1..16 to vulnerability.
            board['vuln'] = Vulnerable[(i%4 + i/4)%4]

        elif isinstance(boardresult, RubberResult):
            belowNS, belowEW = 0, 0  # Running totals of below-the-line scores.
            board['vuln'] = Vulnerable.None
            # Only consider rounds which score below-the-line.
            for result in (r for r in results if r.score.below > 0):
                if result.contract.declarer in (Direction.North, Direction.South):
                    belowNS += result.score.below
                    pair = Vulnerable.NorthSouth
                else:
                    belowEW += result.score.below
                    pair = Vulnerable.EastWest
                # If either score exceeds 100, pair has made game.
                if belowNS >= 100 or belowEW >= 100:
                    belowNS, belowEW = 0, 0  # Reset totals for next game.
                    # Vulnerability transitions.
                    if board['vuln'] == Vulnerable.None:
                        board['vuln'] = pair
                    elif board['vuln'] in (pair, Vulnerable.All):
                        board['vuln'] = Vulnerable.None
                    else:  # Pair was not vulnerable, but other pair was.
                        board['vuln'] = Vulnerable.All

        return board

