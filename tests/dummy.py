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


import os, sys

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


import random, sha
from twisted.cred import credentials
from twisted.internet import reactor
from twisted.spread import pb


from pybridge.common.game import Game

# Set up reconstruction of objects from server.
from pybridge.common.call import Bid, Pass, Double, Redouble
from pybridge.common.card import Card
pb.setUnjellyableForClass(Card, Card)
pb.setUnjellyableForClass(Bid, Bid)
pb.setUnjellyableForClass(Pass, Pass)
pb.setUnjellyableForClass(Double, Double)
pb.setUnjellyableForClass(Redouble, Redouble)

# Enumerations.
from pybridge.common.call import Level, Strain
from pybridge.common.deck import Seat


class DummyBot(pb.Referenceable):

	def __init__(self, username, password):
		self.factory = pb.PBClientFactory()
		self.username = username
		self.password = sha.new(password).hexdigest()
		self.run()

	def run(self):
		
		def connected(perspective):
			self.connection = perspective
		
		def findTable(r):
			d = self.connection.callRemote('listTables')
			return d

		reactor.connectTCP("localhost", 5040, self.factory)
		creds = credentials.UsernamePassword(self.username, self.password)
		d = self.factory.login(creds, self)
		d.addCallback(connected)
		d.addCallback(findTable)
		d.addCallback(self.getTable)


	def getTable(self, tablelist):

		def gotTable(table):
			self.table = table
			self.tablename = tablename
			print "at table %s" % tablename
			self.table.callRemote('listPlayers').addCallback(gotPlayerList)

		def gotPlayerList(players):
			free = [seat for seat, player in players.items() if player==None]
			if len(free) > 0:
				self.seat = getattr(Seat, free[0])
				self.table.callRemote('sitPlayer', str(self.seat)).addCallback(setReady)

		def setReady(x):
			print x
			self.table.callRemote('setReadyFlag', True)

		if len(tablelist) > 0:
			command, tablename = 'joinTable', tablelist[0]
		else:
			command, tablename = 'hostTable', 'dummytable'
		
		d = self.connection.callRemote(command, tablename, listener=self)
		d.addCallback(gotTable)


	def remote_gameStarted(self, dealer):

		def gotHand(hand):
			self.game.deal[self.seat] = hand
		
		deal = dict.fromkeys(Seat, [])  # Unknown cards.
		dealer = getattr(Seat, dealer)
		self.game = Game(dealer, deal, None, False, False)
		
		d = self.table.callRemote('getHand', str(self.seat))
		d.addCallback(gotHand)
		
		if self.game.whoseTurn() == self.seat:
			self.makeCall()


	def remote_gameContract(self, contract):
		print "contract:", contract
		if self.game.whoseTurn() == self.seat:
			reactor.callLater(0.5, self.playCard, self.seat)


	def remote_gameCallMade(self, seat, call):
		seat = getattr(Seat, seat)
		self.game.makeCall(seat, call)
		print "%s calls %s" % (seat, call)
		
		if self.game.whoseTurn() == self.seat:
			if not self.game.bidding.isComplete():
				reactor.callLater(0.2, self.makeCall)


	def remote_gameCardPlayed(self, seat, card):
		declarer = self.game.playing.declarer
		dummy = self.game.playing.dummy
		
		def gotDummyHand(hand):
			self.game.deal[dummy] = hand
			print "got dummy's hand"
		
		seat = getattr(Seat, seat)
		self.game.playing.playCard(card)
		print "%s plays %s" % (seat, card)
		
		# Dummy's hand becomes visible after the first card is played.
		if self.game.deal[dummy] == []:
			print "getting dummy's hand"
			self.table.callRemote('getHand', str(dummy)).addCallback(gotDummyHand)

		seat = self.seat
		if self.game.whoseTurn() == dummy and self.seat == declarer:
			seat = dummy
		
		if self.game.whoseTurn() == seat:
			reactor.callLater(0.2, self.playCard, seat)


	def makeCall(self):
		current = self.game.bidding.currentCall(Bid)
		if current:
			if current.level < Level.Three:
				strain = Strain[(current.strain.index + 1) % 5]
				level = Level[current.level.index + int(strain.index==0)]
				call = Bid(level, strain)
			else:
				call = Pass()
		else:  # Start the bidding.
			call = Bid(Level.One, Strain.Club)
		
		print "my turn: calling %s" % call
		self.table.callRemote('makeCall', call)


	def playCard(self, seat):
		hand = self.game.deal[seat]
		valid = []
		for card in hand:
			if self.game.playing.isValidPlay(card, seat, hand):
				valid.append(card)
		
		print valid
		card = valid[0]
		print "my turn: playing %s", card
		if card in self.game.deal[self.seat]:
			print "card in my hand"
		elif card in self.game.deal[self.game.playing.dummy]:
			print "card in dummy's hand"
		self.table.callRemote('playCard', card)


# Some required, but unused, events.

	def remote_userLoggedIn(self, username):
		print "%s logged in" % username

	def remote_userLoggedOut(self, username):
		print "%s logged out" % username

	def remote_tableOpened(self, tablename):
		print "table %s opened" % tablename

	def remote_tableClosed(self, tablename):
		print "table %s closed" % tablename

	def remote_userJoins(self, username):
		print "user %s joined this table" % username

	def remote_userLeaves(self, username):
		print "user %s left this table" % username

	def remote_playerSits(self, username, seat):
		print "user %s sits %s" % (username, seat)

	def remote_playerStands(self, username, seat):
		print "user %s stands %s" % (username, seat)

	def remote_gameEnded(self):
		print "game ended"
		self.game = None
		self.table.callRemote('setReadyFlag', True)

	def remote_gameResult(self, result):
		print "game result", result


# Utility?

	def handleError(self, error):
		print error, error.getErrorMessage()

	def generateCall(self, lastCall=None):
		if isinstance(lastCall, Bid):
			strain = Strain[(lastCall.strain.index + 1) % 5]
			level = Level[lastCall.level.index + int(strain.index==0)]
			return Bid(level, strain)
		else:
			return Pass()

	def chooseCard(self, prev):
		return self.hand.pop()


if __name__ == '__main__':
	dummy = DummyBot(sys.argv[1], sys.argv[2])
	reactor.run()

