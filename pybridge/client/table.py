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

from pybridge.common.call import Call, Bid, Pass, Double, Redouble
from pybridge.common.card import Card
from pybridge.common.game import Game

# Set up reconstruction of objects from server.
pb.setUnjellyableForClass(Card, Card)
pb.setUnjellyableForClass(Bid, Bid)
pb.setUnjellyableForClass(Pass, Pass)
pb.setUnjellyableForClass(Double, Double)
pb.setUnjellyableForClass(Redouble, Redouble)

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
		
		def gotObservers(observers):
			self.observers = observers
		
		def gotPlayers(players):
			for seat, player in players.items():
				if player is not None:
					self.remote_playerSits(player, seat)
		
		self.remote.callRemote('listObservers').addCallback(gotObservers)
		self.remote.callRemote('listPlayers').addCallback(gotPlayers)
		
		windowmanager.launch('window_game')
		d = self.setupGame()
		return d


	def setupGame(self):
		""""""
		
		def gotGame(info):
			print "got game", info
			if info.get('active'):
				deal = dict.fromkeys(Seat, [])  # Unknown cards.
				dealer = getattr(Seat, info['dealer'])
				self.game = Game(dealer, deal, None, False, False)
			
				calls = info.get('calls', [])
				for call in calls:
					self.game.bidding.addCall(call)
				
				tricks = info.get('played', {})
				for seat in tricks:
					pass
#					leader, cards = trick[0], trick[1:]
#					print leader, cards
#					for card in cards:
#						self.game.playing.playCard(card)
				for seat in Seat:
					self.updateCardArea(seat)
		
		d = self.remote.callRemote('getGame')
		d.addCallback(gotGame)
		return d


	def getHand(self, seat):
		""""""
		
		def gotHand(hand):
			self.game.deal[seat] = hand
			return hand
		
		d = self.remote.callRemote('getHand', seat=str(seat))
		d.addCallback(gotHand)
		return d


	def updateCardArea(self, seat):
		"""Redraws cards of seat.
		
		Cards played are omitted.
		Unknown cards are drawn face-down.
		"""
		print "building cards for ", seat
		hand = self.game.deal[seat]
		if hand and self.game.playing:  # Some cards may be played.
			cards = []
			for card in hand:
				if card in self.game.playing.played[seat]:
					cards.append(None)
				else:
					cards.append(card)
		elif hand:  # Bidding; no cards played.
			cards = hand
		else:  # Unknown hands.
			unplayed = 13
			cards = [None] * unplayed
		
		window = windowmanager.get('window_main')
		window.cardarea.draw_hand(seat, cards)


# Client request methods.


	def sitPlayer(self, seat):
		d = self.remote.callRemote('sitPlayer', seat=str(seat))
		self.seated = seat
		if self.game:
			d.addCallback(lambda r: self.getHand(seat))
			d.addCallback(lambda r: self.updateCardArea(seat))
			if not self.game.bidding.isComplete():
				bidbox = windowmanager.launch('window_bidbox')
				bidbox.set_available_calls(self.seated, self.game.bidding)
		return d


	def standPlayer(self):
		d = self.remote.callRemote('standPlayer')
		self.seated = None
		if self.game and not self.game.bidding.isComplete():
			windowmanager.terminate('window_bidbox')
		return d


	def makeCall(self, call):
		if self.game.whoseTurn() == self.seated and \
		   self.game.bidding.validCall(call):
			d = self.remote.callRemote('makeCall', call=call)
			return d


	def playCard(self, card):
		if self.game and self.game.playing and self.game.whoseTurn() == self.seated and \
		   self.game.playing.isValidPlay(card, self.seated, self.game.deal[self.seated]):
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
		if self.game:
			self.game.makeCall(seat, call)
			windowmanager.get('window_game').add_call(call, seat)
			if self.seated:
				bidbox = windowmanager.get('window_bidbox')
				bidbox.set_available_calls(self.seated, self.game.bidding)
			
			if self.game.whoseTurn() == self.seated:
				print "my turn"


	def remote_gameCardPlayed(self, seat, card):
		print "%s plays %s" % (seat, card)
		seat = getattr(Seat, seat)
		if self.game:
			play = self.game.playing
			play.playCard(card)  # Manipulate play directly.
			
			# Redraw current trick.
			trick = play.getTrick(play.currentTrick())[1]
			window = windowmanager.get('window_main')
			window.cardarea.draw_trick(trick)
			
			self.updateCardArea(seat)
			# Dummy's hand becomes visible after the first card is played.


	def remote_gameContract(self, contract):
		print contract
		if self.seated:
			windowmanager.terminate('window_bidbox')


	def remote_gameEnded(self):
		print "ended"


	def remote_gameResult(self, result):
		print result


	def remote_gameStarted(self, dealer):
		windowmanager.get('window_game').reset_bidding()
		d = self.setupGame()
		if self.seated:
			d.addCallback(lambda r: self.getHand(self.seated))
			windowmanager.launch('window_bidbox')
		d.addCallback(lambda r: self.updateCardArea(self.seated))

