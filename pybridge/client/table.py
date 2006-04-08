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

from windowmanager import windowmanager

from pybridge.common.call import Call
from pybridge.common.card import Card
from pybridge.common.game import Game

# Set up reconstruction of objects from server.
pb.setUnjellyableForClass(Call, Call)
pb.setUnjellyableForClass(Card, Card)

# Enumerations.
from pybridge.common.deck import Seat


class ClientBridgeTable(pb.Referenceable):
	"""Representation of a table, from a client POV."""


	def __init__(self, name):
		self.name = name
		self.remote = None  # Server-side Table object.
		
		self.game = None
		self.observers = []
		self.players = dict.fromkeys(Seat, None)
		self.playing = None


	def setup(self, info):
		print info
		self.observers.extend(info['observers'])  # OK?
		for seatname, player in info['players'].items():
			self.players[getattr(Seat, seatname)] = player


# Client request methods.


	def sitPlayer(self, seat):
		if not self.playing:
			d = self.remote.callRemote('sitPlayer', seat=str(seat))
			d.addCallback(lambda r: setattr(self, 'playing', seat))
			return d


	def standPlayer(self):
		if self.playing:
			d = self.remote.callRemote('standPlayer')
			d.addCallback(lambda r: setattr(self, 'playing', None))
			return d


	def makeCall(self, call):
		if self.playing and self.game:
			d = self.remote.callRemote('makeCall', call)
			return d


	def playCard(self, card):
		if self.playing and self.game:
			d = self.remote.callRemote('playCard', card)
			return d


# Remote methods, visible by server-side Table object.


	def remote_userJoins(self, username):
		self.observers.append(username)
		print "%s joins this table" % username


	def remote_userLeaves(self, username):
		self.observers.remove(username)
		print "%s leaves this table" % username


	def remote_playerSits(self, username, seat):
		seat = getattr(Seat, seat)
		self.players[seat] = username
		print "player %s sits %s" % (username, seat)
		windowmanager.get('window_game').player_sits(username, seat)


	def remote_playerStands(self, username, seat):
		seat = getattr(Seat, seat)
		self.players[seat] = None
		print "player %s stands %s" % (username, seat)
		windowmanager.get('window_game').player_stands(username, seat)


	def remote_gameCallMade(self, seat, call):
		seat = getattr(Seat, seat)
		self.game.makeCall(seat, call)
		print seat, call


	def remote_gameCardPlayed(self, seat, card):
		seat = getattr(Seat, seat)
		self.game.playCard(seat, card)
		print seat, card


	def remote_gameContract(self, contract):
		print contract


	def remote_gameEnded(self):
		print "ended"


	def remote_gameResult(self, result):
		print result


	def remote_gameStarted(self, dealer):
		deal = {Seat.North : [], Seat.East : [], Seat.South : [], Seat.West : []}
		self.game = Game(dealer, deal, None, False, False)
		
		if self.playing:  # Get my hand.
			d = self.remote.callRemote('getHand', str(self.playing))
			d.addCallback(lambda hand: deal.__setitem__(self.playing, hand))  # Will this work?
		
		windowmanager.get('window_main').gameStarted()
		print "gamestarted %s" % dealer

