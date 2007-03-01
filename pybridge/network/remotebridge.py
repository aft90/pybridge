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
from zope.interface import implements

from pybridge.interfaces.bridgetable import IBridgeTable
from pybridge.network.remotetable import RemoteTable
from pybridge.network.error import DeniedRequest, IllegalRequest

# Set up reconstruction of objects from server.
from pybridge.bridge.call import Bid, Pass, Double, Redouble
from pybridge.bridge.card import Card
pb.setUnjellyableForClass(Bid, Bid)
pb.setUnjellyableForClass(Pass, Pass)
pb.setUnjellyableForClass(Double, Double)
pb.setUnjellyableForClass(Redouble, Redouble)
pb.setUnjellyableForClass(Card, Card)

# Bridge game.
from pybridge.bridge.game import Game, GameError
from pybridge.bridge.scoring import scoreDuplicate
from pybridge.bridge.symbols import Player


class RemoteBridgeTable(RemoteTable):
    """A bridge table, implementing the IBridgeTable interface.
    
    This is a cache of a remote MasterBridgeTable.
    """

    implements(IBridgeTable)


    def __init__(self):
        RemoteTable.__init__(self)
        
        self.dealer = None
        self.game = None
        self.players = dict.fromkeys(Player, None)
        self.scoring = scoreDuplicate


    def setCopyableState(self, state):
        RemoteTable.setCopyableState(self, state)
        
        # Convert seat strings to Player enumeration values.
        players = {}
        for seat, player in self.players.items():
            players[getattr(Player, seat)] = player
        self.players = players
        
        if state.get('game'):
            self.dealer = getattr(Player, state['game']['dealer'])  # XX
            deal = {}
            for player in Player:
                deal[player] = state['game']['deal'].get(player, [])
            vulnNS, vulnEW = state['game']['vulnNS'], state['game']['vulnEW']
            self.game = Game(self.dealer, deal, self.scoring, vulnNS, vulnEW)
            if state['game'].get('calls'):
                for call in state['game']['calls']:
                    player = self.game.whoseTurn()
                    self.game.makeCall(call=call, player=player)
            if state['game'].get('played'):
                played = state['game']['played']
                while sum([len(cards) for cards in played.values()]) > 0:
                    player = self.game.whoseTurn()
                    card = played[player.key].pop(0)
                    self.game.playCard(card=card, player=player)


    def gameMakeCall(self, call, position=None):
        d = self.master.callRemote('gameMakeCall', call)
        return d

#        # Check that game is running and we are playing.
#        if self.game and self.game.whoseTurn() == self.position \
#        and self.game.bidding.validCall(call):
#            # TODO: bidding.isValidCall() should check turn to bid.
#            d = self.master.callRemote('gameMakeCall', call)
#            return d


    def gamePlayCard(self, card, position):
        d = self.master.callRemote('gamePlayCard', card)
        return d


    def requestNextGame(self, ready=True, player=None):
        d = self.master.callRemote('requestNextGame', ready)
        return d


# Remote update methods.


    def observe_gameStarted(self, dealer, vulnNS, vulnEW):
        dealer = getattr(Player, dealer)  # XX
        self.dealer = dealer
        deal = dict.fromkeys(Player, [])  # Unknown hands.
        self.game = Game(dealer, deal, self.scoring, vulnNS, vulnEW)
        self.eventHandler.gameStarted(self, dealer, vulnNS, vulnEW)


    def observe_gameFinished(self):
        self.eventHandler.gameFinished(self)


    def observe_gameCallMade(self, call, position):
        position = getattr(Player, position)  # XX
        self.game.makeCall(call=call, player=position)
        self.eventHandler.gameCallMade(self, call, position)


    def observe_gameCardPlayed(self, card, position):
        position = getattr(Player, position)  # XX
        self.game.playCard(card=card, player=position)
        self.eventHandler.gameCardPlayed(self, card, position)


    def observe_gameHandRevealed(self, hand, position):
        position = getattr(Player, position)  # XX
        self.game.deal[position] = hand
        self.eventHandler.gameHandRevealed(self, hand, position)

