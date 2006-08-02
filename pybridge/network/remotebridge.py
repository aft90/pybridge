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

# Enumerations.
from pybridge.bridge.deck import Seat


class RemoteBridgeTable(RemoteTable):
    """A bridge table, implementing the IBridgeTable interface.
    
    This is a cache of a remote MasterBridgeTable.
    """

    implements(IBridgeTable)


    def __init__(self):
        RemoteTable.__init__(self)
        
        self.dealer = None
        self.game = None
        self.players = dict.fromkeys(Seat, None)
        self.scoring = scoreDuplicate


    def setCopyableState(self, state):
        RemoteTable.setCopyableState(self, state)
        
        # Convert seat strings to Seat enumeration values.
        players = {}
        for seat, player in self.players.items():
            players[getattr(Seat, seat)] = player
        self.players = players
        
        if state.get('game'):
            self.dealer = getattr(Seat, state['game']['dealer'])  # XX
            deal = {}
            for seat in Seat:
                deal[seat] = state['game']['deal'].get(seat, [])
            vulnNS, vulnEW = state['game']['vulnNS'], state['game']['vulnEW']
            self.game = Game(self.dealer, deal, self.scoring, vulnNS, vulnEW)
            if state['game'].get('calls'):
                for call in state['game']['calls']:
                    seat = self.game.whoseTurn()
                    self.game.makeCall(call=call, seat=seat)
            if state['game'].get('played'):
                played = state['game']['played']
                while sum([len(cards) for cards in played.values()]) > 0:
                    seat = self.game.whoseTurn()
                    card = played[seat.key].pop(0)
                    self.game.playCard(card=card, seat=seat)


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
#        # Check that game is running, we are playing,
#        # the position specified is on turn to play,
#        # and the card specified is in player's hand.
#        if self.game and self.position \
#        and self.game.whoseTurn() == position \
#        and self.game.playing.isValidPlay(card, position, self.game.deal[position]):
#            d = self.master.callRemote('gamePlayCard', card)
#            return d
#            declarer = self.game.playing.declarer
#            dummy = self.game.playing.dummy
#            # Can play card from own hand, or from dummy's hand as declarer.
#            seat = 
#            if self.game.whoseTurn() == self.position \
#            or (self.game.whoseTurn() == dummy and self.position == declarer):
#                d = self.master.callRemote('gamePlayCard', card)
#                return d


    def requestNextGame(self, ready=True, player=None):
        d = self.master.callRemote('requestNextGame', ready)
        return d


# Remote update methods.


    def observe_gameStarted(self, dealer, vulnNS, vulnEW):
        dealer = getattr(Seat, dealer)  # XX
        self.dealer = dealer
        deal = dict.fromkeys(Seat, [])  # Unknown hands.
        self.game = Game(dealer, deal, self.scoring, vulnNS, vulnEW)
        self.eventHandler.gameStarted(self, dealer, vulnNS, vulnEW)


    def observe_gameFinished(self):
        self.eventHandler.gameFinished(self)


    def observe_gameCallMade(self, call, position):
        position = getattr(Seat, position)  # XX
        self.game.makeCall(call=call, seat=position)
        self.eventHandler.gameCallMade(self, call, position)


    def observe_gameCardPlayed(self, card, position):
        position = getattr(Seat, position)  # XX
        self.game.playCard(card=card, seat=position)
        self.eventHandler.gameCardPlayed(self, card, position)


    def observe_gameHandRevealed(self, hand, position):
        position = getattr(Seat, position)  # XX
        self.game.deal[position] = hand
        self.eventHandler.gameHandRevealed(self, hand, position)

