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
from scoring import scoreDuplicate

from call import Bid, Pass, Double, Redouble
from card import Card
from symbols import Direction, Suit, Strain, Vulnerable


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
        self.visibleHands = {}  # A subset of deal, containing revealed hands.
        self.players = {}  # One-to-one mapping from BridgePlayer to Direction.


# Implementation of ICardGame.


    def start(self, board=None):
        if self.inProgress():
            raise GameError, "Game in progress"

        if board:  # Use specified board.
            self.board = board
        elif self.board:  # Advance to next deal.
            self.board.nextDeal(result=self)  # TODO: proper GameResult object.
        else:  # Create a board.
            self.board = Board()
            self.board.nextDeal()
        self.bidding = Bidding(self.board['dealer'])  # Start bidding.
        self.contract = None
        self.play = None
        self.visibleHands.clear()

        # Remove deal from board, so it does not appear to clients.
        visibleBoard = self.board.copy()
        visibleBoard['deal'] = self.visibleHands

        self.notify('start', board=visibleBoard)


    def inProgress(self):
        if self.play:
            return not self.play.isComplete()
        elif self.bidding:
            return not self.bidding.isPassedOut()
        else:
            return False


    def isNextGameReady(self):
        return (not self.inProgress()) and len(self.players) == 4


    def getState(self):
        state = {}

        if self.inProgress():
            # Remove hidden hands from deal.
            visibleBoard = self.board.copy()
            visibleBoard['deal'] = self.visibleHands
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

            for call in state.get('calls', []):
                turn = self.getTurn()
                self.makeCall(call, position=turn)

            for card in state.get('played', []):
                turn = self.getTurn()
                # TODO: remove this hack
                if turn == self.play.dummy:
                    turn = self.play.declarer
                self.playCard(card, position=turn)


    def updateState(self, event, *args, **kwargs):
        allowed = ['start', 'makeCall', 'playCard', 'revealHand']
        if event in allowed:
            try:
                handler = getattr(self, event)
                handler(*args, **kwargs)
            except GameError, e:
                print "Unexpected error when updating game state:", e


    def addPlayer(self, position):
        if position not in Direction:
            raise TypeError, "Expected Direction, got %s" % type(position)
        if position in self.players.values():
            raise GameError, "Position %s is taken" % position

        player = BridgePlayer(self)
        self.players[player] = position
        self.notify('addPlayer', position=position)

        return player


    def removePlayer(self, position):
        if position not in Direction:
            raise TypeError, "Expected Direction, got %s" % type(position)
        if position not in self.players.values():
            raise GameError, "Position %s is vacant" % position

        for player, pos in self.players.items():
            if pos == position:
                del self.players[player]
                break

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


    def makeCall(self, call, player=None, position=None):
        """Make a call in the current bidding session.
        
        This method expects to receive either a player argument or a position.
        If both are given, the position argument is disregarded.
        
        @param call: a Call object.
        @type call: Bid or Pass or Double or Redouble
        @param player: if specified, a player object.
        @type player: BridgePlayer or None
        @param position: if specified, the position of the player making call.
        @type position: Direction or None
        """
        if not isinstance(call, (Bid, Pass, Double, Redouble)):
            raise TypeError, "Expected Call, got %s" % type(call)
        if player:
            if player not in self.players:
                raise GameError, "Player unknown to this game"
            position = self.players[player]
        if position not in Direction:
            raise TypeError, "Expected Direction, got %s" % type(position)

        # Validate call according to game state.
        if not self.bidding or self.bidding.isComplete():
            raise GameError, "No game in progress, or bidding complete"
        if self.getTurn() != position:
            raise GameError, "Call made out of turn"
        if not self.bidding.isValidCall(call, position):
            raise GameError, "Call cannot be made"

        self.bidding.makeCall(call, position)

        if self.bidding.isComplete() and not self.bidding.isPassedOut():
            self.contract = self.bidding.getContract()  # TODO: make a property
            trumpSuit = self.trumpMap[self.contract['bid'].strain]
            self.play = Playing(self.contract['declarer'], trumpSuit)

        self.notify('makeCall', call=call, position=position)

        # If bidding is passed out, reveal all hands.
        if not self.inProgress() and self.board['deal']:
            for position in Direction:
                hand = self.board['deal'].get(position)
                if hand and position not in self.visibleHands:
                    self.revealHand(hand, position)


    def signalAlert(self, alert, position):
        pass  # TODO


    def playCard(self, card, player=None, position=None):
        """Play a card in the current play session.
        
        This method expects to receive either a player argument or a position.
        If both are given, the position argument is disregarded.
        
        If position is specified, it must be that of the player of the card:
        declarer plays cards from dummy's hand when it is dummy's turn.
        
        @param card: a Card object.
        @type card: Card
        @param player: if specified, a player object.
        @type player: BridgePlayer or None
        @param position: if specified, the position of the player of the card.
        @type position: Direction or None
        """
        if not isinstance(card, Card):
            raise TypeError, "Expected Card, got %s" % type(card)
        if player:
            if player not in self.players:
                raise GameError, "Invalid player reference"
            position = self.players[player]
        if position not in Direction:
            raise TypeError, "Expected Direction, got %s" % type(position)

        if not self.play or self.play.isComplete():
            raise GameError, "No game in progress, or play complete"

        playfrom = position

        # Declarer controls dummy's turn.
        if self.getTurn() == self.play.dummy:
            if position == self.play.declarer:
                playfrom = self.play.dummy  # Declarer can play from dummy.
            elif position == self.play.dummy:
                raise GameError, "Dummy cannot play hand"

        if self.getTurn() != playfrom:
            raise GameError, "Card played out of turn"

        hand = self.board['deal'].get(playfrom, [])  # Empty if hand unknown.
        if not self.play.isValidPlay(card, playfrom, hand):
            raise GameError, "Card cannot be played from hand"

        self.play.playCard(card)
        self.notify('playCard', card=card, position=position)

        # Dummy's hand is revealed when the first card of first trick is played.
        if len(self.play.getTrick(0)[1]) == 1:
            dummyhand = self.board['deal'].get(self.play.dummy)
            if dummyhand:  # Reveal hand only if known.
                self.revealHand(dummyhand, self.play.dummy)

        # If play is complete, reveal all hands.
        if not self.inProgress() and self.board['deal']:
            for position in Direction:
                hand = self.board['deal'].get(position)
                if hand and position not in self.visibleHands:
                    self.revealHand(hand, position)
 

    def revealHand(self, hand, position):
        """Reveal hand to all observers.
        
        @param hand: a hand of Card objects.
        @type hand: list
        @param position: the position of the hand.
        @type position: Direction
        """
        if position not in Direction:
            raise TypeError, "Expected Direction, got %s" % type(position)

        self.visibleHands[position] = hand
        # Add hand to board only if it was previously unknown.
        if not self.board['deal'].get(position):
            self.board['deal'][position] = hand

        self.notify('revealHand', hand=hand, position=position)


    def getHand(self, position):
        """If specified hand is visible, returns the list of cards in hand.
        
        @param position: the position of the requested hand.
        @type position: Direction
        @return: the hand of player at position.
        """
        if position not in Direction:
            raise TypeError, "Expected Direction, got %s" % type(position)

        if self.board and self.board['deal'].get(position):
            return self.board['deal'][position]
        else:
            raise GameError, "Hand unknown"


    def getTurn(self):
        if self.inProgress():
            if self.bidding.isComplete():  # In trick play.
                return self.play.whoseTurn()
            else:  # Currently in the bidding.
                return self.bidding.whoseTurn()
        else:  # Not in game.
            raise GameError, "No game in progress"


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
        dummy = Direction[(declarer.index + 2) % 4]

        if declarer in (Direction.North, Direction.South):
            vulnerable = (self.board['vuln'] in (Vulnerable.NorthSouth, Vulnerable.All))
        else:  # East or West
            vulnerable = (self.board['vuln'] in (Vulnerable.EastWest, Vulnerable.All))

        tricksMade = 0  # Count of tricks won by declarer or dummy.
        for index in range(len(self.play.winners)):
            trick = self.play.getTrick(index)
            winningCard = self.play.winningCard(trick)
            winner = self.play.whoPlayed(winningCard)
            tricksMade += winner in (declarer, dummy)
        result = {'contract'   : contract,
                  'tricksMade' : tricksMade,
                  'vulnerable' : vulnerable, }
        return scoreDuplicate(result)




class BridgePlayer(pb.Referenceable):
    """Actor representing a player's view of a BridgeGame object."""


    def __init__(self, game):
        self.__game = game  # Access to game is private to this object.


    def getHand(self):
        position = self.__game.players[self]
        return self.__game.getHand(position)


    def makeCall(self, call):
        try:
            return self.__game.makeCall(call, player=self)
        except TypeError, e:
            raise GameError, e


    def playCard(self, card):
        try:
            return self.__game.playCard(card, player=self)
        except TypeError, e:
            raise GameError, e


    def startNextGame(self):
        if not self.__game.isNextGameReady():
            raise GameError, "Not ready to start game"
        self.__game.start()  # Raises GameError if game in progress.


# Aliases for remote-callable methods.

    remote_getHand = getHand
    remote_makeCall = makeCall
    remote_playCard = playCard
    remote_startNextGame = startNextGame

