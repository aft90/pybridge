#!/usr/bin/env python

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


import os
import sys


# Determine the base directory.
currentdir = os.path.dirname(os.path.abspath(sys.argv[0]))
basedir = os.path.abspath(os.path.join(currentdir, '..'))

# Find the Python module path, relative to the base directory.
if os.path.exists(os.path.join(basedir, 'lib')):
	pythonver = 'python%d.%d' % sys.version_info[:2]
	pythonpath = os.path.join(basedir, 'lib', pythonver, 'site-packages')
else:
	pythonpath = basedir

sys.path.insert(0, pythonpath)


import random
from twisted.internet import reactor
from zope.interface import implements

from pybridge.interfaces.table import ITableEvents
from pybridge.interfaces.bridgetable import IBridgeTableEvents
from pybridge.interfaces.serverstate import IServerEvents

from pybridge.network.client import client

from pybridge.bridge.call import Bid, Double, Redouble, Pass
from pybridge.bridge.call import Level, Strain
from pybridge.bridge.deck import Seat


# Give the bot some "personality".
QUOTES = ["Hello!", "Doctor? Doctor? DOCTOR!", "My brain hurts!",
          "Are you the brain specialist?", 
          "No. No, I am not the brain specialist. No I am not. Yes! Yes I am!",
          "Well, I think cement is more interesting than people think!",
          "I believe in peace... and bashing two bricks together.",
          "I would put a tax on all people who stand in water... Oh!", ]

SLOTH = 0.1  # Time between game event and response.


class BotEventHandler:

    implements(IServerEvents, ITableEvents, IBridgeTableEvents)


    def __init__(self):
        self.table = None  # Convenient reference to observed table.


    def errback(self, failure):
        print "ERROR:", failure.getErrorMessage()


# Selection of calls and cards.


    def chooseCall(self):
        
        def makeCall():
            print "My turn: calling %s" % call
            d = self.table.gameMakeCall(call)
            d.addErrback(self.errback)
        
        current = self.table.game.bidding.getCurrentCall(Bid)
        if current:
            if current.level < Level.Three:
                strain = Strain[(current.strain.index + 1) % 5] 
                level = Level[current.level.index + int(strain.index==0)]
                call = Bid(level, strain)
            else:
                call = Pass()
        else:  # Start the bidding.
            call = Bid(Level.One, Strain.Club)
        reactor.callLater(SLOTH, makeCall)


    def chooseCard(self, position):
        
        def playCard():
            print "My turn: playing %s from %s" % (str(selected), position)
            d = self.table.gamePlayCard(selected, position)
            d.addErrback(self.errback)
        
        hand = self.table.game.deal[position]
        if hand:
            valid = [c for c in hand if self.table.game.playing.isValidPlay(c, position, hand)]
            selected = random.choice(valid)
            reactor.callLater(SLOTH, playCard)
        else:  # Hand not revealed just yet, try again a little later.
            reactor.callLater(0.1, self.chooseCard, position)


    def tableOpened(self, table):
       
        def joinedTable(table):
            self.table = table  # Set table reference.
            print "I joined table %s" % table.id
            table.sendMessage(random.choice(QUOTES))

            # Find a vacant seat.
            for seat, player in table.players.items():
                if player is None:
                    table.addPlayer(seat)  # Take seat.
                    break
        
        print "Table %s opened" % table
        if len(client.tables) == 0:  # Not observing any tables.
            d = client.joinTable(table).addCallback(joinedTable)


    def tableClosed(self, table):
        pass


    def userLoggedIn(self, user):
        pass


    def userLoggedOut(self, user):
        pass


# Implementation of ITableEvents.


    def observerAdded(self, table, observer):
        pass


    def observerRemoved(self, table, observer):
        pass


    def playerAdded(self, table, player, position):
        if player == client.username:
            print "I take seat %s" % position
        else:
            print "Player %s takes seat %s" % (player, position)


    def playerRemoved(self, table, player, position):
        print "Player %s leaves seat %s" % (player, position)


    def messageReceived(self, table, message, sender, recipients):
        if sender != client.username:
            print "%s says: %s" % (sender, message)


# Implementation of IBridgeTableEvents.


    def gameStarted(self, table, dealer, vulnNS, vulnEW):
        print "Game started: dealer is %s" % dealer
        if self.table.game.whoseTurn() == self.table.getPositionOfPlayer(client.username):
            self.chooseCall()


    def gameFinished(self, table):
        print "Game finished"


    def gameCallMade(self, table, call, position):
        print "Call %s made by %s" % (call, position)
        if self.table.game.whoseTurn() == self.table.getPositionOfPlayer(client.username):
            if not self.table.game.bidding.isComplete():
                self.chooseCall()
            else:
                myseat = self.table.getPositionOfPlayer(client.username)
                self.chooseCard(myseat)


    def gameCardPlayed(self, table, card, position):
        print "Card %s played by %s" % (card, position)
        
        if not self.table.game.isComplete():
            myseat = self.table.getPositionOfPlayer(client.username)
            turn = self.table.game.whoseTurn()
            if turn == self.table.game.playing.dummy and myseat == self.table.game.playing.declarer:
               myseat = self.table.game.playing.dummy  # Declarer controls dummy.
            if turn == myseat:
                self.chooseCard(myseat)


    def gameHandRevealed(self, table, hand, position):
        print "I can see %s's hand" % position




def lostConnection(connector, reason):
    print "Connection lost: %s" % reason.getErrorMessage()
    reactor.stop()


if __name__ == '__main__':
    username, password = sys.argv[1], sys.argv[2]
    
    client.factory.clientConnectionLost = lostConnection
    client.eventHandler = BotEventHandler()
    client.connect(hostname="localhost", port=5040)
    client.login(username, password)
    
    reactor.run()

