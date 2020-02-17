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

from .symbols import Direction, Strain, Vulnerable


class GameResult(object):
    """Represents the result of a completed round of bridge."""

    _getScore = NotImplemented  # Expected to be implemented by subclasses.

    __vulnMap = {Vulnerable.None: (),
                 Vulnerable.NorthSouth: (Direction.North, Direction.South),
                 Vulnerable.EastWest: (Direction.East, Direction.West),
                 Vulnerable.All: tuple(Direction)}


    def __init__(self, board, contract, tricksMade=None):
        """
        @type board: Board
        @type contract: Contract
        @type tricksMade: int or None
        """
        self.board = board
        self.contract = contract
        self.tricksMade = tricksMade

        self.isVulnerable = None
        if self.contract:
            vuln = self.board.get('vuln', Vulnerable.None)
            self.isVulnerable = self.contract.declarer in self.__vulnMap[vuln]

        self.score = self._getScore()


    def getStateToCopy(self):
        return (self.board.copy(), self.contract, self.tricksMade,
                self.isVulnerable, self.score)


    def setCopyableState(self, state):
        self.board, self.contract, self.tricksMade, self.isVulnerable, self.score = state
        # assert self.score == self._getScore()


    def _getScoreComponents(self):
        """Compute the component values which contribute to the score.
        Note that particular scoring schemes may ignore some of the components.

        Scoring values: http://en.wikipedia.org/wiki/Bridge_scoring

        @return: a dict of component values.
        @rtype: dict
        """
        components = {}

        isDoubled      = bool(self.contract.doubleBy)
        isRedoubled    = bool(self.contract.redoubleBy)
        isVulnerable   = self.isVulnerable
        contractLevel  = self.contract.bid.level.index + 1
        tricksMade     = self.tricksMade
        tricksRequired = contractLevel + 6
        trumpSuit      = self.contract.bid.strain

        if tricksMade >= tricksRequired:  # Contract successful.

            #### Contract tricks (bid and made) ####
            if trumpSuit in (Strain.Club, Strain.Diamond):
                # Clubs and Diamonds score 20 for each odd trick.
                components['odd'] = contractLevel * 20
            else:  # Hearts, Spades and NT score 30 for each odd trick.
                components['odd'] = contractLevel * 30
                if trumpSuit == Strain.NoTrump:
                    components['odd'] += 10  # For NT, add a 10 point bonus.
            if isRedoubled:
                components['odd'] *= 4  # Double the doubled score.
            elif isDoubled:
                components['odd'] *= 2  # Double score.


            #### Overtricks ####
            overTricks = tricksMade - tricksRequired

            if isRedoubled:
                # 400 for each overtrick if vulnerable, 200 if not.
                if isVulnerable:
                    components['over'] = overTricks * 400
                else:
                    components['over'] = overTricks * 200

            elif isDoubled:
                # 200 for each overtrick if vulnerable, 100 if not.
                if isVulnerable:
                    components['over'] = overTricks * 200
                else:
                    components['over'] = overTricks * 100

            else:  # Undoubled contract.
                if trumpSuit in (Strain.Club, Strain.Diamond):
                    # Clubs and Diamonds score 20 for each overtrick.
                    components['over'] = overTricks * 20
                else:
                    # Hearts, Spades and NT score 30 for each overtrick.
                    components['over'] = overTricks * 30


            #### Premium bonuses ####

            if tricksRequired == 13:
                # 1500 for grand slam if vulnerable, 1000 if not.
                if isVulnerable:
                    components['slambonus'] = 1500
                else:
                    components['slambonus'] = 1000

            elif tricksRequired == 12:
                # 750 for small slam if vulnerable, 500 if not.
                if isVulnerable:
                    components['slambonus'] = 750
                else:
                    components['slambonus'] = 500

            elif components['odd'] >= 100:  # Game contract (non-slam).
                # 500 for game if vulnerable, 300 if not.
                if isVulnerable:
                    components['gamebonus'] = 500
                else:
                    components['gamebonus'] = 300

            else:  # Non-game contract.
                components['partscore'] = 50


            #### Insult bonus ####
            if isRedoubled:
                components['insultbonus'] = 100
            elif isDoubled:
                components['insultbonus'] = 50


        else:  # Contract not successful.

            underTricks = tricksRequired - tricksMade

            if isRedoubled:
                if isVulnerable:
                    # -400 for first, then -600 each.
                    components['under'] = -400 + (underTricks - 1) * -600
                else:
                    # -200 for first, -400 for second and third, then -600 each.
                    components['under'] = -200 + (underTricks - 1) * -400
                    if underTricks > 3:
                        components['under'] += (underTricks - 3) * -200

            elif isDoubled:
                if isVulnerable:
                    # -200 for first, then -300 each.
                    components['under'] = -200 + (underTricks - 1) * -300
                else:
                    # -100 for first, -200 for second and third, then -300 each.
                    components['under'] = -100 + (underTricks - 1) * -200
                    if underTricks > 3:
                        components['under'] += (underTricks - 3) * -100
            else:
                if isVulnerable:
                    # -100 each.
                    components['under'] = underTricks * -100
                else:
                    # -50 each.
                    components['under'] = underTricks * -50

        return components




class DuplicateResult(GameResult, pb.Copyable, pb.RemoteCopy):
    """Represents the result of a completed round of duplicate bridge."""


    def _getScore(self):
        """Duplicate bridge scoring scheme.
        
        @return: score value: positive for declarer, negative for defenders.
        """
        score = 0
        if self.contract and self.tricksMade:
            for key, value in list(self._getScoreComponents().items()):
                if key in ('odd', 'over', 'under', 'slambonus', 'gamebonus',
                           'partscore', 'insultbonus'):
                    score += value
        return score


pb.setUnjellyableForClass(DuplicateResult, DuplicateResult)




class RubberResult(GameResult, pb.Copyable, pb.RemoteCopy):
    """Represents the result of a completed round of rubber bridge."""


    def _getScore(self):
        """Rubber bridge scoring scheme.
        
        @return: 2-tuple of numeric scores (above the line, below the line):
                 positive for declarer, negative for defenders.
        """
        above, below = 0, 0
        if self.contract and self.tricksMade:
            for key, value in list(self._getScoreComponents().items()):
                # Note: gamebonus/partscore are not assigned in rubber bridge.
                if key in ('over', 'under', 'slambonus', 'insultbonus'):
                    above += value
                elif key == 'odd':
                    below += value
        return above, below


pb.setUnjellyableForClass(RubberResult, RubberResult)




class Rubber(list):
    """A rubber set, in which pairs compete to make two consecutive games.
    
    A game is made by accumulation of 100+ points from below-the-line scores
    without interruption from an opponent's game.
    """

    games = property(lambda self: self._getGames())
    winner = property(lambda self: self._getWinner())


    def _getGames(self):
        """Returns a list of completed (ie. won) 'games' in this rubber, in the
        order of their completion.
        
        A game is represented as a list of consecutive results from this rubber,
        coupled with the identifier of the scoring pair.
        """
        games = []

        thisgame = []
        belowNS, belowEW = 0, 0  # Cumulative totals for results in this game.

        for result in self:
            thisgame.append(result)
            if result.contract.declarer in (Direction.North, Direction.South):
                belowNS += result.score[1]
                if belowNS >= 100:
                    games.append((thisgame, (Direction.North, Direction.South)))
            else:
                belowEW += result.score[1]
                if belowEW >= 100:
                    games.append((thisgame, (Direction.East, Direction.West)))

            # If either total for this game exceeds 100, proceed to next game.
            if belowNS >= 100 or belowEW >= 100:  
                thisgame = []
                belowNS, belowEW = 0, 0  # Reset accumulators.

        return games


    def _getWinner(self):
        """The rubber is won by the pair which have completed two games."""
        pairs = [pair for game, pair in self.games]

        for pair in ((Direction.North, Direction.South), (Direction.East, Direction.West)):
            if pairs.count(pair) >= 2:
                return pair

