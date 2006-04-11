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


	def __init__(self):
		self.remote = None  # Server-side Table object.
		
		self.game = None
		self.observers = []
		self.players = dict.fromkeys(Seat, None)
		self.seated = False  # If playing, the seat occupied.


	def setup(self):
		""""""
		windowmanager.launch('window_game')
		
		def gotObservers(observers):
			self.observers = observers
		
		def gotPlayers(players):
			for seat, player in players.items():
				if player is not None:
					self.remote_playerSits(player, seat)
		
		self.remote.callRemote('listObservers').addCallback(gotObservers)
		self.remote.callRemote('listPlayers').addCallback(gotPlayers)
		d = self.setupGame()
		d.addCallback(lambda r: self.updateCardArea())
		return d


	def setupGame(self):
		""""""
		
		def gotGame(info):
			print "got game", info
			if info.get('active'):
				deal = dict.fromkeys(Seat, [None]*13)  # Unknown cards.
				dealer = getattr(Seat, info['dealer'])
				self.game = Game(dealer, deal, None, False, False)
			
				calls = info.get('calls', [])
				for call in calls:
					self.game.bidding.addCall(call)
				
				tricks = info.get('tricks', [])
				for trick in tricks:
					leader, cards = trick[0], trick[1:]
					print leader, cards
					for card in cards:
						self.game.play.playCard(card)
		
		d = self.remote.callRemote('getGame')
		d.addCallback(gotGame)
		return d


	def getHand(self, seat):
		""""""
		
		def gotHand(hand):
			self.game.deal[seat] = hand
			return hand
		
		d = self.remote.callRemote('getHand', str(seat))
		d.addCallback(gotHand)
		return d


	def updateCardArea(self):
		window = windowmanager.get('window_main')
		if self.game:
			for seat, cards in self.game.deal.items():
				window.cardarea.build_hand_pixbuf(seat, cards)


# Client request methods.


	def sitPlayer(self, seat):
		d = self.remote.callRemote('sitPlayer', seat=str(seat))
		self.seated = seat
		if self.game:
			d.addCallback(lambda r: self.getHand(seat))
			d.addCallback(lambda r: self.updateCardArea())
		return d


	def standPlayer(self):
		d = self.remote.callRemote('standPlayer')
		self.seated = None
		return d


	def makeCall(self, call):
		d = self.remote.callRemote('makeCall', call=call)
		return d


	def playCard(self, card):
		d = self.remote.callRemote('playCard', card=card)
		return d


# Remote methods, callable by server-side Table object.


	def remote_userJoins(self, username):
		self.observers.append(username)


	def remote_userLeaves(self, username):
		self.observers.remove(username)


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
		d = self.setupGame()
		if self.seated:
			d.addCallback(lambda r: self.getHand(self.seated))
			windowmanager.launch('window_bidbox')
		d.addCallback(lambda r: self.updateCardArea())


# Utility.



