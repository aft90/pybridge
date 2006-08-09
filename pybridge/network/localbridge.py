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


from twisted.internet import reactor
from twisted.spread import pb
from zope.interface import implements

from pybridge.interfaces.bridgetable import IBridgeTable
from pybridge.network.error import DeniedRequest, IllegalRequest
from pybridge.network.localtable import LocalTable, LocalTableViewable

# Set up reconstruction of objects from clients.
from pybridge.bridge.call import Bid, Pass, Double, Redouble
from pybridge.bridge.card import Card
pb.setUnjellyableForClass(Bid, Bid)
pb.setUnjellyableForClass(Pass, Pass)
pb.setUnjellyableForClass(Double, Double)
pb.setUnjellyableForClass(Redouble, Redouble)
pb.setUnjellyableForClass(Card, Card)

# Bridge game.
from pybridge.bridge.deck import Deck
from pybridge.bridge.game import Game, GameError
from pybridge.bridge.scoring import scoreDuplicate

# Enumerations.
from pybridge.bridge.deck import Seat


class LocalBridgeTable(LocalTable):
    """A bridge table, implementing the IBridgeTable interface.
    
    """

    implements(IBridgeTable)  # Also ITable, from parent Table.


    def __init__(self, id):
        LocalTable.__init__(self, id)
        self.view = LocalBridgeTableViewable(self)  # For clients.
        
        self.dealer = None
        self.deck = Deck()
        self.game = None
        self.players = dict.fromkeys(Seat, None)
        self.scoring = scoreDuplicate
        
        self.handsSeen = {}
        for seat in Seat:
            self.handsSeen[seat] = []
        
        self.pendingDeals = []   # Queue of deals for successive games.
        
        # A time delay between a finished game and starting the next game.
        self.config['gameWaitInterval'] = 5


    def getState(self):
        state = LocalTable.getState(self)
        
        if self.game:
            state['game'] = {}
            state['game']['dealer'] = self.dealer.key
            state['game']['vulnNS'] = self.game.vulnNS
            state['game']['vulnEW'] = self.game.vulnEW
            if self.game.bidding:
                state['game']['calls'] = self.game.bidding.calls
            if self.game.playing:
                state['game']['declarer'] = self.game.playing.declarer.key
                state['game']['played'] = {}
                for seat, played in self.game.playing.played.items():
                    state['game']['played'][seat.key] = played
            # Add visible hands.
            state['game']['deal'] = {}
            for seat, hand in self.game.deal.items():
                if self.game.isHandVisible(seat, viewer=None):
                    state['game']['deal'][seat.key] = hand
        else:
            state['game'] = None
        
        return state


    def addPlayer(self, position, player):
        # Overrides LocalTable, to provision revealHands() and testStartGame().
        LocalTable.addPlayer(self, position, player)
        
        self.handsSeen[position] = []  # Clear list of hands seen by player.
        if self.game:  # If game in progress...
            self.revealHands()  # ... provide player with visible hands.
        # Test if game is ready to start.
        self.testStartGame()
        


# Methods implementing IBridgeTable.


    def gameMakeCall(self, call, position):
        if self.game is None or self.game.isComplete():
            raise DeniedRequest, 'Game not running'
        elif position is None:
            raise DeniedRequest, 'Not a player'
        
        try:
            self.game.makeCall(call=call, seat=position)
        except GameError, error:
            raise DeniedRequest, error
        
        self.updateObservers('gameCallMade', call=call, position=position.key)
        self.testEndGame()


    def gamePlayCard(self, card, position):
        if self.game is None or self.game.isComplete():
            raise DeniedRequest, 'Game not running'
        elif position is None:
            raise DeniedRequest, 'Not a player'
        elif self.game.playing is None:
            raise DeniedRequest, 'Play not running'
        
        # Declarer can play dummy's cards, dummy cannot play own cards.
        if self.game.whoseTurn() == self.game.playing.dummy:
            if position == self.game.playing.declarer:  # Declarer commands dummy.
                position = self.game.playing.dummy
            elif position == self.game.playing.dummy:
                raise DeniedRequest, 'Dummy cannot play cards'
        
        try:
            self.game.playCard(card=card, seat=position)
        except GameError, error:
            raise DeniedRequest, error
        
        self.updateObservers('gameCardPlayed', card=card, position=position.key)
        self.revealHands()
        self.testEndGame()


    def requestNextGame(self, player, ready=True):
        self.observers[player]['ready'] = (ready == True)
        self.testStartGame()  # Check to start game.


# Utility methods.


    def testStartGame(self, dealer=None, deal=None):
        """If no game is active and all players are ready, start a game."""
        if (self.game is None or self.game.isComplete()) \
        and len([p for p in self.players.values() if p is None]) == 0:
            
            deal = deal or self.deck.dealRandom()
            vulnNS, vulnEW = False, False
            self.dealer = dealer or (self.dealer and Seat[(self.dealer.index + 1) % 4]) or Seat.North
            self.game = Game(self.dealer, deal, self.scoring, vulnNS, vulnEW)
            self.updateObservers('gameStarted', dealer=self.dealer.key, vulnNS=vulnNS, vulnEW=vulnEW)
            
            for position in self.handsSeen:
                self.handsSeen[position] = []  # Clear lists of hands seen.
            self.revealHands()  # Provide players with their hands.
            return True
        return False


    def testEndGame(self):
        """If game is finished, end game."""
        if self.game and self.game.isComplete():
            self.updateObservers('gameFinished')
            self.revealHands()  # Make all hands visible.
            
            # Set up time delay before next game starts.
            wait = self.config.get('gameWaitInterval', 0)
            reactor.callLater(wait, self.testStartGame)
            
            return True
        return False


    def revealHands(self):
        """
        
        Each hand is transmitted only once to each player.
        """
        # TODO: what about observers?
        for viewer, player in self.players.items():
            for seat in Seat:
                if seat not in self.handsSeen[viewer] and self.game.isHandVisible(seat, viewer):
                    self.handsSeen[viewer].append(seat)
                    hand = self.game.deal[seat]
                    self.informObserver(self.observers[player], 'gameHandRevealed',
                                        hand=hand, position=seat.key)




class LocalBridgeTableViewable(LocalTableViewable):


    def view_gameMakeCall(self, user, call, position=None):
        position = self.table.getPositionOfPlayer(user)
        self.table.gameMakeCall(call, position)


    def view_gamePlayCard(self, user, card, position=None):
        position = self.table.getPositionOfPlayer(user)
        self.table.gamePlayCard(card, position)

