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
from pybridge.common.scoring import scoreDuplicate

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
		self.seated = False  # If playing, the seat we occupy.


	def setup(self):
		""""""
		
		def gotObservers(observers):
			self.observers = observers
			window = windowmanager.get('window_game')
			window.add_observers(observers)
		
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
				self.game = Game(dealer, deal, scoreDuplicate, False, False)
				setupBidding(info.get('calls', []))
				setupPlaying(info.get('played', {}))
				for seat in Seat:
					self.redrawHand(seat)
		
		def setupBidding(calls):
			window = windowmanager.get('window_game')
			for call in calls:
				seat = self.game.whoseTurn()
				self.game.makeCall(seat, call)
				window.add_call(call, seat)
			if self.game.bidding.contract():
				window.set_contract(self.game.bidding.contract())
		
		def setupPlaying(played):
			while sum([len(cards) for cards in played.values()]) > 0:
				seat = self.game.whoseTurn()
				card = played[str(seat)].pop(0)
				self.game.playCard(seat, card)
			if self.game.playing:
				if len(self.game.playing.getTrick(0)) >= 1:
					d = self.getHand(self.game.playing.dummy)
					d.addCallback(lambda r: self.redrawHand(self.game.playing.dummy))
				self.redrawTrick(self.game.playing.currentTrick())
		
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


	def redrawHand(self, seat, all=False):
		"""Redraws cards making up the hand of player at seat.
		
		Cards played are omitted. Unknown cards are drawn face-down.
		"""
		hand = self.game.deal[seat]
		played = self.game.playing and self.game.playing.played[seat] or []
		
		if hand and all==True:  # Own or known hand: show all cards.
			cards = hand
		elif hand:  # Own or known hand: filter out cards played.
			cards = [((card not in played and card) or None) for card in hand]
		else:  # Unknown hand.
			cards = ['facedown']*(13-len(played)) + [None]*len(played)
		
		# dummy = self.game.playing != None and seat == self.game.playing.dummy
		# transpose = dummy and seat in (Seat.North, Seat.South)
		window = windowmanager.get('window_main')
		window.cardarea.build_hand(seat, cards) # , transpose, dummy)
		window.cardarea.draw_hand(seat)


	def redrawTrick(self, trickindex):
		"""Draws trick."""
		trick = self.game.playing.getTrick(trickindex)
		
		window = windowmanager.get('window_main')
		window.cardarea.build_trick(trick)
		window.cardarea.draw_trick()


# Client request methods.


	def sitPlayer(self, seat):
		d = self.remote.callRemote('sitPlayer', seat=str(seat))
		self.seated = seat
		d.addCallback(lambda r: self.setReadyFlag())
		if self.game:
			d.addCallback(lambda r: self.getHand(seat))
			d.addCallback(lambda r: self.redrawHand(seat))
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
		if self.game.whoseTurn() == self.seated and self.game.bidding.validCall(call):
			d = self.remote.callRemote('makeCall', call=call)
			return d


	def playCard(self, card):
		seat = self.seated
		if self.game and self.game.playing:
			dummy, declarer = self.game.playing.dummy, self.game.playing.declarer
			# Declarer can play dummy's cards.
			if self.game.whoseTurn() == dummy and seat == declarer:
				seat = dummy
			if self.game.playing.isValidPlay(card, seat, self.game.deal[seat]):
				d = self.remote.callRemote('playCard', card=card)
				return d


	def setReadyFlag(self):
		d = self.remote.callRemote('setReadyFlag', True)
		return d


# Remote methods, callable by server-side Table object.


	def remote_userJoins(self, username):
		if self.observers:
			self.observers.append(username)
			windowmanager.get('window_game').add_observers((username, ))


	def remote_userLeaves(self, username):
		if self.observers:
			self.observers.remove(username)
			windowmanager.get('window_game').remove_observers((username, ))


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
			windowmanager.get('window_main').set_turn(self.game.whoseTurn())
			if self.seated:
				bidbox = windowmanager.get('window_bidbox')
				bidbox.set_available_calls(self.seated, self.game.bidding)


	def remote_gameCardPlayed(self, seat, card):
		seat = getattr(Seat, seat)
		play = self.game.playing
		trickindex = play.currentTrick()  # Preserve trick index.
		
		# Since hands may be unknown, bypass isValidCard() check.
		play.playCard(card)
		leader, trick = play.getTrick(trickindex)
		
		# Dummy's hand becomes visible after the first card is played.
		if play.currentTrick() == 0 and len(trick) == 1:
			d = self.getHand(play.dummy)
			d.addCallback(lambda r: self.redrawHand(play.dummy))
		
		# Redraw current trick.
		self.redrawHand(seat)
		self.redrawTrick(trickindex)  # Using preserved trick index.
		
		# Update trick counters in window_game.
		dclWon, dclReq = 0, 0  # Declarer won and required tricks.
		defWon, defReq = 0, 0  # Defence won and required tricks.
		for index in range(play.currentTrick()):
			winner = play.whoPlayed(play.winningCard(index))
			dclWon += int(winner in (play.declarer, play.dummy))
			defWon += int(winner not in (play.declarer, play.dummy))
		required = self.game.bidding.contract()['bid'].level.index + 7
		dclReq = int(required > dclWon and required - dclWon)
		defReq = int(13-required+1 > defWon and 13 - required - defWon + 1)
		window = windowmanager.get('window_game')
		window.set_wontricks((dclWon, dclReq), (defWon, defReq))
		windowmanager.get('window_main').set_turn(self.game.whoseTurn())


	def remote_gameContract(self, contract):
		if self.seated:
			windowmanager.terminate('window_bidbox')
		contract = self.game.bidding.contract()
		windowmanager.get('window_game').set_contract(contract)


	def remote_gameEnded(self):
		windowmanager.get('window_main').set_turn(None)
		window = windowmanager.get('window_game')
		
		if self.game.playing and self.game.playing.isComplete():
			# Display cards in order played.
			for seat, cards in self.game.playing.played.items():
				self.game.deal[seat] = cards
				self.redrawHand(seat, all=True)
			# Determine score.
			contract = self.game.bidding.contract()
			offset = -(self.game.bidding.contract()['bid'].level.index + 7)
			for index in range(13):  # Add on won (made) tricks.
				winner = self.game.playing.whoPlayed(self.game.playing.winningCard(index))
				offset += int(winner in (self.game.playing.declarer, self.game.playing.dummy))
		
		elif self.game.bidding.isPassedOut():
			if self.seated:
				windowmanager.terminate('window_bidbox')
			# Fetch other hands.
			for seat in self.game.deal:
				d = self.getHand(seat)
				d.addCallback(lambda _: self.redrawHand(seat, all=True))
			# Null contract and trick offset.
			contract = None
			offset = 0
			
		score = self.game.score()
		window = windowmanager.get('window_game')
		window.set_result(contract, offset, score)


	def remote_gameStarted(self, dealer):
		window = windowmanager.get('window_game')
		window.reset_game()
		
		d = self.setupGame()
		if self.seated:
			bidbox = windowmanager.launch('window_bidbox')
			d.addCallback(lambda r: self.getHand(self.seated))
			d.addCallback(lambda r: bidbox.set_available_calls(self.seated, self.game.bidding))
		d.addCallback(lambda r: self.redrawHand(self.seated))
		d.addCallback(lambda r: windowmanager.get('window_main').set_turn(self.game.whoseTurn()))

