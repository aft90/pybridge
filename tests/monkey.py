#!/usr/bin/env python

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
import time
from twisted.internet import reactor
from zope.interface import implements

from pybridge.interfaces.observer import IListener

from pybridge.network.client import NetworkClient
from pybridge.network.error import GameError

from pybridge.bridge.call import Bid, Double, Redouble, Pass
from pybridge.bridge.card import Card
from pybridge.bridge.symbols import Level, Strain, Rank, Suit


# Give the bot some "personality".
QUOTES = ["Hello!", "Doctor? Doctor? DOCTOR!", "My brain hurts!",
          "Are you the brain specialist?", 
          "No. No, I am not the brain specialist. No I am not. Yes! Yes I am!",
          "Well, I think cement is more interesting than people think!",
          "I believe in peace... and bashing two bricks together.",
          "I would put a tax on all people who stand in water... Oh!", ]

SLOTH = 0.1  # Time between game event and response.


class SimpleEventHandler:

    implements(IListener)

    def __init__(self, target):
        self.target = target

    def update(self, event, *args, **kwargs):
        method = getattr(self.target, "event_%s" % event, None)
        if method:
            method(*args, **kwargs)


class Monkey:
    """Simulation of a monkey playing bridge.
    
    The monkey will attempt to make calls and play cards at random, disregarding
    the rules of bridge (playing in turn, following suit, etc). Only valid
    calls and cards should be accepted by the Game object.

    For inspiration, see:
    http://folklore.org/StoryView.py?project=Macintosh&story=Monkey_Lives.txt
    """


    def __init__(self, client):
        self.client = client
        self.table = None  # RemoteTable.
        self.player = None  # RemoteReference to remote BridgePlayer object.
        self.position = None


    def success(self, r):
        pass


    def errback(self, failure):
        if failure.type == str(GameError):
            pass  # Suppress GameErrors.
            # TODO: command-line option
        else:
            print "ERROR:", failure.getErrorMessage()


    def connected(self, r):
        print "Logged in to server"
        reactor.callLater(0.2, self.joinTable)


    def joinTable(self):
        print "Looking for a table to join..."
        if self.client.tableRoster.get('Monkey'):
            d = self.client.joinTable('Monkey')
        else:
            d = self.client.joinTable('Monkey', host=True)
        d.addCallbacks(self.joinedTable, self.errback)


    def joinedTable(self, table):
        self.table = table  # Set table reference.
        self.table.attach(SimpleEventHandler(self))
        self.table.game.attach(SimpleEventHandler(self))

        print "I joined table %s" % table.id
        table.sendMessage(random.choice(QUOTES))

        # Find a vacant place at the table, if any.
        for position in table.game.positions:
            if table.players.get(position) is None:
                d = table.joinGame(position)  # Take seat.
                d.addCallbacks(self.joinedGame, self.errback,
                               callbackArgs=[position])
                break


    def joinedGame(self, player, position):
        self.player = player
        self.position = position

        d = self.player.callRemote('startNextGame')
        d.addErrback(self.errback)


# Selection of calls and cards.


    calls = [Bid(random.choice(Level), random.choice(Strain)),
             Pass(), Double(), Redouble()]

    def chooseCall(self):
        call = random.choice(self.calls)
        d = self.player.callRemote('makeCall', call)  # TODO
        d.addCallbacks(self.success, self.errback)


    #cards = [Card(r, s) for r in Rank for s in Suit]

    def chooseCard(self):
        turn = self.table.game.getTurn()
        try:
            hand = self.table.game.getHand(turn)
            card = random.choice(hand)
            d = self.player.callRemote('playCard', card)  # TODO
            d.addCallbacks(self.success, self.errback)
        except GameError:
            pass


# IServerEvents


    def tableOpened(self, table):
        print "Table %s opened" % table


    def tableClosed(self, table):
        print "Table %s closed" % table


    def userLoggedIn(self, user):
        print "User %s logged in" % user


    def userLoggedOut(self, user):
        print "User %s logged out" % user


# Table events.


    def event_joinGame(self, player, position):
        if player == self.client.username:
            print "I take seat %s" % position
        else:
            print "Player %s takes seat %s" % (player, position)


    def event_leaveGame(self, player, position):
        print "Player %s leaves seat %s" % (player, position)


    def event_sendMessage(self, message, sender, recipients):
        if sender == self.client.username:
            print "I say: %s" % message
        else:
            print "%s says: %s" % (sender, message)


# Game events.


    def event_start(self, board):

        def gotHand(hand):
            print "My hand is", [str(c) for c in hand]
            self.table.game.revealHand(hand, self.position)

        def loop():
            if self.table.game.inProgress():
                if not self.table.game.bidding.isComplete():
                    self.chooseCall()
                else:
                    self.chooseCard()
                reactor.callLater(SLOTH, loop)
            else:
                print "Game terminated"

        print "Game started: dealer is %s" % board['dealer']
        if self.player:
            d = self.player.callRemote('getHand')
            d.addCallbacks(gotHand, self.errback)
            loop()


    def event_makeCall(self, call, position):
        print "%s made by %s" % (call, position)


    def event_playCard(self, card, position):
        print "%s played by %s" % (card, position)


    def event_revealHand(self, hand, position):
        print "Hand of %s revealed" % position


client = NetworkClient()


def loginFailed(reason):
    print "Login failed: %s" % reason.getErrorMessage()
    client.disconnect()


def lostConnection(connector, reason):
    print "Connection lost: %s" % reason.getErrorMessage()
    reactor.stop()


if __name__ == '__main__':
    username, password = sys.argv[1], sys.argv[2]

    client.factory.clientConnectionLost = lostConnection
    client.eventHandler = Monkey(client)

    client.connect("localhost", 5040)
    d = client.login(username, password)
    d.addCallbacks(client.eventHandler.connected, loginFailed)

    reactor.run()

