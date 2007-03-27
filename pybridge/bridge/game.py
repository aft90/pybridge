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


from twisted.spread import pb
from zope.interface import implements

from pybridge.interfaces.game import ICardGame
from pybridge.interfaces.observer import ISubject
from pybridge.network.error import GameError

from bidding import Bidding
from board import Board
from playing import Playing

from symbols import Direction, Suit, Strain


class BridgeGame(object):
    """A bridge game models the bidding and play sequence.
    
    The methods of this class comprise the interface of a state machine.
    Clients should only use the class methods to interact with the game state.
    Modifications to the state are typically made through BridgePlayer objects.
    
    Methods which change the game state (makeCall, playCard) require a player
    argument as "authentication".
    """

    implements(ICardGame, ISubject)


    # Valid positions.
    positions = Direction

    # Mapping from Strain symbols (in bidding) to Suit symbols (in play).
    trumpMap = {Strain.Club: Suit.Club, Strain.Diamond: Suit.Diamond,
                Strain.Heart: Suit.Heart, Strain.Spade: Suit.Spade,
                Strain.NoTrump: None}


    def __init__(self):
        self.listeners = []

        self.board = None
        self.bidding = None
        self.contract = None
        self.play = None

        self.boardQueue = []  # Boards for successive games.
        self.players = {}  # One-to-one mapping from Direction to BridgePlayer.


# Implementation of ICardGame.


    def start(self, board=None):
        if board:  # Use specified board.
            self.board = board
        elif self.board:  # Advance to next deal.
            self.board.nextDeal(result=999)
        else:  # Create a board.
            self.board = Board()
            self.board.nextDeal()
        self.bidding = Bidding(self.board['dealer'])  # Start bidding.
        self.contract = None
        self.play = None

        # Remove deal from board, so it does not appear to players.
        visibleBoard = self.board.copy()
        del visibleBoard['deal']
        self.notify('start', board=visibleBoard)


    def inProgress(self):
        if self.play:
            return not self.play.isComplete()
        elif self.bidding:
            return not self.bidding.isPassedOut()
        else:
            return False


    def getState(self):
        # TODO: all flag?
        state = {}

        if self.inProgress():
            # Remove deal from board, so it does not appear to players.
            visibleBoard = self.board.copy()
            del visibleBoard['deal']
            state['board'] = visibleBoard

        if self.bidding:
            state['calls'] = self.bidding.calls
        if self.play:
            state['played'] = []
            trickcount = max([len(s) for s in self.play.played.values()])
            for index in range(trickcount):
                leader, cards = self.play.getTrick(index)
                for pos in Direction[leader.index:] + Direction[:leader.index]:
                    if pos in cards:
                        state['played'].append(cards[pos])

        return state


    def setState(self, state):
        if state.get('board'):
            self.start(state['board'])

            # Comprehensive error checking is suppressed.
            for call in state.get('calls', []):
                turn = self.getTurn()
                self.makeCall(call, self.players[turn])
#                self.bidding.makeCall(call, player=turn)

            # If a contract has been reached, start the play.
#            contract = self.bidding.getContract()
#            if contract:
#                self.contract = contract
#                trumpSuit = self.trumpMap[self.contract['bid'].strain]
#                self.play = Playing(contract['declarer'], trumpSuit)

            # Comprehensive error checking is suppressed.
            for card in state.get('played', []):
                turn = self.getTurn()
                self.playCard(card, self.players[turn])
                #self.play.playCard(card, player=turn)


    def updateState(self, event, *args, **kwargs):
        allowed = ['start', 'makeCall', 'playCard']
        if event in allowed:
            handler = getattr(self, event)
            handler(*args, **kwargs)
#        else:
#            print "updateState unknown attempted", event


    def addPlayer(self, position):
        if position not in Direction:
            raise TypeError, "Expected Direction, got %s" % type(position)
        if position in self.players:
            raise GameError, "Position %s is taken" % position

        player = BridgePlayer(self)
        self.players[position] = player
        self.notify('addPlayer', position=position)

        return player


    def removePlayer(self, position):
        if position not in Direction:
            raise TypeError, "Expected Direction, got %s" % type(position)
        if position not in self.players:
            raise GameError, "Position %s is vacant" % position

        player = self.players[position]
        del self.players[position]
        self.notify('removePlayer', position=position)


# Implementation of ISubject.


    def attach(self, listener):
        self.listeners.append(listener)


    def detach(self, listener):
        self.listeners.remove(listener)


    def notify(self, event, *args, **kwargs):
        for listener in self.listeners:
            listener.update(event, *args, **kwargs)


# Bridge-specific methods.


    def makeCall(self, call, player):
        """Make a call in the current bidding session.
        
        @param call: the call.
        @type call: Bid or Pass or Double or Redouble
        @param player: a player identifier.
        @type player: BridgePlayer
        """
        position = self.getPositionOfPlayer(player)
        if position is None:
            raise GameError, "Invalid player reference"

        # Validate call according to game state.
        if not self.bidding or self.bidding.isComplete():
            raise GameError, "Game not running or bidding complete"
        if self.getTurn() is not position:
            raise GameError, "Call made out of turn"
        if not self.bidding.isValidCall(call, position):
            raise GameError, "Call cannot be made"

        self.bidding.makeCall(call, position)
        self.notify('makeCall', call=call, position=position)

        if self.bidding.isComplete():
            # If a contract has been reached, start the play.
            contract = self.bidding.getContract()
            if contract:
                self.contract = contract
                trumpSuit = self.trumpMap[self.contract['bid'].strain]
                self.play = Playing(contract['declarer'], trumpSuit)
            elif self.bidding.isPassedOut():
                self.notify('gameOver')


    def signalAlert(self, alert, player):
        pass  # TODO


    def playCard(self, card, player):
        """Play a card in the current play session.
        
        @param card: a Card object.
        @param player: a BridgePlayer object.
        """
        position = self.getPositionOfPlayer(player)
        if position is None:
            raise GameError, "Invalid player reference"
        if not self.play or self.play.isComplete():
            raise GameError, "Game not running or play complete"

        if self.getTurn() is self.play.dummy:  # Dummy's turn.
            if position is self.play.declarer:
                position = self.play.dummy  # Declarer can play dummy's cards.
            elif position is self.play.dummy:
                raise GameError, "Dummy cannot play cards"
        elif self.getTurn() is not position:
            raise GameError, "Card played out of turn"

        hand = self.board['deal'][position]  # May be empty, if hand unknown.
        if not self.play.isValidPlay(card, position, hand):
            raise GameError, "Card cannot be played from hand"

        self.play.playCard(card)
        self.notify('playCard', card=card, position=position)


    def getHand(self, position, player):
        """If specified hand is visible, returns the list of cards in hand.
        
        A hand is visible if one of the following conditions is met:
        
        1. The hand is the player's own hand.
        2. The game is finished.
        3. The bidding is complete and the hand is dummy's, and first card of
           first trick has been played.
        
        @param position: the hand identifier.
        @type position: Direction
        @param player: a player identifier.
        @type player: BridgePlayer
        """
        viewer = self.getPositionOfPlayer(player)
        if viewer is None:
            raise GameError, "Invalid player reference"
        if not self.inProgress() and self.bidding is None:
            raise GameError, "No game in progress"

        if player == viewer or not self.inProgress():
            return self.board.deal[position]
        if self.bidding.isComplete() and position == self.play.dummy:
            leader, cards = self.play.getTrick(0)
            if len(cards) >= 1:
                return self.board.deal[position]

        # At this point, checks have been exhausted.
        raise GameError, "Hand is not visible"


    def getTurn(self):
        if self.inProgress():
            if self.play:  # Currently in the play.
                return self.play.whoseTurn()
            else:  # Currently in the bidding.
                return self.bidding.whoseTurn()
        else:  # Not in game.
            raise GameError, "No game in progress"


    def getTrickCount(self):
        """Returns various
        
        @return: a dictionary of result information.
        @rtype: dict
        
        
        ['declarerWon']: number of tricks won by declarer/dummy.
        @return['defenceWon']: number of tricks won by defenders.
        @return['declarerNeeds']: number of extra tricks required by declarer
                                  to make contract.
        @return['defenceNeeds']: number of extra tricks required by defenders
                                 to break contract.
        @return['required']: number of tricks required from contract level.
        
        """
        if self.play is None:
            raise GameError, "Not in play"
        
        count = dict.fromkeys(('declarerWon', 'declarerNeeds',
                               'defenceWon', 'defenceNeeds'), 0)
        
        for index in range(len(self.play.winners)):
            trick = self.play.getTrick(index)
            winner = self.play.whoPlayed(self.play.winningCard(trick))
            if winner in (self.play.declarer, self.play.dummy):
                count['declarerWon'] += 1
            else:  # Trick won by defenders.
                count ['defenceWon'] += 1
        
        contract = self.bidding.getContract()
        # Get index value of bid level, increment, add 6.
        count['required'] = contract['bid'].level.index + 7
        count['declarerNeeds'] = max(0, count['required'] - count['declarerWon'])
        count['defenceNeeds'] = max(0, 13 - count['required'] - count['defenceWon'] + 1)
        
        return count


    def getScore(self):
        """Returns the integer score value for declarer/dummy if:

        - bidding stage has been passed out, with no bids made.
        - play stage is complete.
        """
        if self.inProgress() or self.bidding is None:
            raise GameError, "Game not complete"
        if self.bidding.isPassedOut():
            return 0  # A passed out deal does not score.

        contract = self.bidding.getContract()
        declarer = contract['declarer']
        dummy = Seat[(declarer.index + 2) % 4]
        vulnerable = (self.vulnNS and declarer in (Seat.North, Seat.South)) + \
                     (self.vulnEW and declarer in (Seat.West, Seat.East))

        tricksMade = 0  # Count of tricks won by declarer or dummy.
        for index in range(len(self.play.winners)):
            trick = self.play.getTrick(index)
            winningCard = self.play.winningCard(trick)
            winner = self.play.whoPlayed(winningCard)
            tricksMade += winner in (declarer, dummy)
        result = {'contract'   : contract,
                  'tricksMade' : tricksMade,
                  'vulnerable' : vulnerable, }
        return self.scoring(result)


    def getPositionOfPlayer(self, player):
        """If player is playing, returns position of player, otherwise None.
        
        @param player: a BridgePlayer object.
        @type player: BridgePlayer
        @return: the position of player.
        @rtype: Direction or None
        """
        for position, p in self.players.items():
            if p == player:
                return position
        return None




class BridgePlayer(pb.Referenceable):
    """Actor representing a player's view of a BridgeGame object."""


    def __init__(self, game):
        self.__game = game  # Provide access to game only through this object.


    def makeCall(self, call):
        self.__game.makeCall(call, player=self)


    def playCard(self, card):
        self.__game.playCard(card, player=self)


    def nextGame(self):
        pass


# Aliases for remote-callable methods.


    def remote_makeCall(self, call):
        self.makeCall(call)


    def remote_playCard(self, card):
        self.playCard(card)

