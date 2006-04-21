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
			if info.get('active'):
				deal = dict.fromkeys(Seat, [])  # Unknown cards.
				dealer = getattr(Seat, info['dealer'])
				self.game = Game(dealer, deal, None, False, False)
				setupBidding(info.get('calls', []))
				setupPlaying(info.get('played', {}))
				for seat in Seat:
					self.updateCardArea(seat)
		
		def setupBidding(calls):
			for call in calls:
				seat = self.game.whoseTurn()
				self.game.makeCall(seat, call)
			if self.game.bidding.contract():
				window = windowmanager.get('window_game')
				window.set_contract(self.game.bidding.contract())
		
		def setupPlaying(played):
			while sum([len(cards) for cards in played.values()]) > 0:
				seat = self.game.whoseTurn()
				card = played[str(seat)].pop(0)
				self.game.playCard(seat, card)
		
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
			if self.game.playing:
				played = len(self.game.playing.played[seat])
			else:
				played = 0
			unplayed = 13 - played
			cards = ['facedown']*unplayed + [None]*played
		
		window = windowmanager.get('window_main')
		window.cardarea.build_hand(seat, cards)
		window.cardarea.draw_hand(seat)


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
		windowmanager.get('window_game').player_sits(username, seat)


	def remote_playerStands(self, username, seat):
		seat = getattr(Seat, seat)
		self.players[seat] = None
		windowmanager.get('window_game').player_stands(username, seat)


	def remote_gameCallMade(self, seat, call):
		seat = getattr(Seat, seat)
		if self.game:
			self.game.makeCall(seat, call)
			windowmanager.get('window_game').add_call(call, seat)
			if self.seated:
				bidbox = windowmanager.get('window_bidbox')
				bidbox.set_available_calls(self.seated, self.game.bidding)


	def remote_gameCardPlayed(self, seat, card):
		seat = getattr(Seat, seat)
		play = self.game.playing
		
		# Since hands may be unknown, bypass isValidCard() check.
		play.playCard(card)
		trick = play.getTrick(play.currentTrick())
		dummy = Seat[(play.declarer.index + 2) % 4]
		
		# Dummy's hand becomes visible after the first card is played.
		if play.currentTrick() == 0 and len(trick[1]) == 1:
			self.getHand(dummy)
		
		# Redraw current trick.
		window = windowmanager.get('window_main')
		self.updateCardArea(seat)
		window.cardarea.build_trick(trick)
		window.cardarea.draw_trick()
		
		# Update trick counters in window_game.
		dclWon, dclReq = 0, 0  # Declarer won and required tricks.
		defWon, defReq = 0, 0  # Defence won and required tricks.
		for index in range(play.currentTrick()):
			winner = play.whoPlayed(play.winningCard(index))
			dclWon += int(winner in (play.declarer, dummy))
			defWon += int(winner not in (play.declarer, dummy))
		required = self.game.bidding.contract()['bid'].level.index + 7
		dclReq = int(required > dclWon and required - dclWon)
		defReq = int(13-required+1 > defWon and 13 - required - defWon + 1)
		window = windowmanager.get('window_game')
		window.set_wontricks((dclWon, dclReq), (defWon, defReq))


	def remote_gameContract(self, contract):
		if self.seated:
			windowmanager.terminate('window_bidbox')
		contract = self.game.bidding.contract()
		windowmanager.get('window_game').set_contract(contract)


	def remote_gameEnded(self):
		window = windowmanager.get('window_game')
		window.reset_contract()
		window.reset_wontricks()


	def remote_gameResult(self, result):
		print result


	def remote_gameStarted(self, dealer):
		windowmanager.get('window_game').reset_bidding()
		d = self.setupGame()
		if self.seated:
			d.addCallback(lambda r: self.getHand(self.seated))
			windowmanager.launch('window_bidbox')
		d.addCallback(lambda r: self.updateCardArea(self.seated))

