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

from pybridge.common.call import Call, Bid, Pass, Double, Redouble
from pybridge.common.card import Card
from pybridge.common.deck import Deck
from pybridge.common.game import Game
from pybridge.common.scoring import scoreDuplicate

# Enumerations.
from pybridge.common.deck import Seat

from pybridge.failure import *

# Set up reconstruction of game objects from client.
pb.setUnjellyableForClass(Card, Card)
pb.setUnjellyableForClass(Bid, Bid)
pb.setUnjellyableForClass(Pass, Pass)
pb.setUnjellyableForClass(Double, Double)
pb.setUnjellyableForClass(Redouble, Redouble)


class BridgeTable(pb.Viewable):
	"""A bridge table sits four players."""
	# TODO: perhaps subclass Table, facilitating tables for different card games.


	def __init__(self, name, server):
		self.name = name
		self.server = server
		
		# Set up bridge-related stuff.
		self.dealer    = None  # Rotate around the table for each deal.
		self.deck      = Deck()
		self.game      = None
		self.observers = {}  # For each observing user name, its remote listener object.
		self.players   = dict.fromkeys(Seat, None)
		self.scoring   = scoreDuplicate  # A function.


# Observer and player methods.


	def addObserver(self, username, listener):
		"""Adds user to list of observers."""
		self.observers[username] = listener
		self.informObservers('userJoins', username=username)


	def removeObserver(self, username):
		"""Removes user from list of observers."""
		del self.observers[username]
		
		# If user was a player, then unseat player.
		seat = self.getSeatForPlayer(username)
		if seat:
			self.players[seat] = None
			self.informObservers('playerStands', username=username, seat=str(seat))
		
		self.informObservers('userLeaves', username=username)
		# If there are no remaining observers, we should close table.
		if len(self.observers) == 0:
			self.server.tableClose(self.name)


	def startGame(self, dealer=None, deal=None):
		"""Called to start a game."""
		deal = deal or self.deck.dealRandom()
		dealer = dealer or self.dealer
		self.game = Game(dealer, deal, self.scoring, vulnNS=False, vulnEW=False)
		self.informObservers('gameStarted', dealer=str(self.dealer))
		self.dealer = Seat[(dealer.index + 1) % 4]  # For next game.


	def endGame(self):
		"""Called to terminate a game, when:
		
		- the bidding has been passed out without a contract.
		- the play has been completed.
		"""
		# TODO: get score.
		self.informObservers('gameEnded')
		self.game = None


# Remote methods.


	def view_listObservers(self, user):
		"""Returns a list of all observer names at table."""
		return self.observers.keys()


	def view_listPlayers(self, user):
		"""Returns a dict of player names, keyed by seat."""
		players = {}  # Convert seat enumerations to strings.
		for seat, username in self.players.items():
			players[str(seat)] = username
		return players


	def view_sitPlayer(self, user, seat):
		"""Allocates seat to user if:
		
		- user is not already playing at the table.
		- the specified seat is empty.
		"""
		if seat not in Seat:
			raise InvalidParameterError()
		elif user.name in self.players.values():  # User already playing.
			raise TablePlayingError()
		
		seat = getattr(Seat, seat)
		if self.players[seat] is not None:  # Seat occupied.
			raise TableSeatOccupiedError()
		
		self.players[seat] = user.name
		self.informObservers('playerSits', username=user.name, seat=str(seat))

		playerCount = len([p for p in self.players.values() if p != None])
		# If player is first person to sit at table, then make player dealer.
		if self.dealer is None or playerCount == 1:
			self.dealer = seat
		
		# If all seats filled, and no game is currently running, start a game.
		elif self.game is None and playerCount == 4:
			self.startGame()


	def view_standPlayer(self, user):
		"""Removes user from seat, provided user occupies seat."""
		seat = self.getSeatForPlayer(user.name)
		if seat is None:  # User not playing.
			raise TablePlayingError()
		
		self.players[seat] = None
		self.informObservers('playerStands', username=user.name, seat=str(seat))


	def view_getGame(self, user):
		"""Returns sufficient information to reconstruct a Game object."""
		info = {}
		info['active'] = self.game != None
		if self.game:
			info['turn'] = str(self.game.whoseTurn())
			if self.game.bidding:
				info['calls'] = self.game.bidding.calls
				info['dealer'] = str(self.game.bidding.dealer)
			if self.game.playing:
				info['declarer'] = str(self.game.playing.declarer)
				info['played'] = {}
				for seat, cards in self.game.playing.played.items():
					info['played'][str(seat)] = cards
		return info


	def view_getHand(self, user, seat):
		"""Returns the hand of player at seat, or DeniedRequest if hand is hidden.
		
		If user is a player, then their ability to view the hand will be examined.
		"""
		if seat not in Seat:
			raise InvalidParameterError()
		elif self.game is None:
			raise RequestUnavailableError()
		
		seat = getattr(Seat, seat)
		# If user is not a player, then player == None.
		player = self.getSeatForPlayer(user.name)
		return self.game.getHand(seat, player)


	def view_makeCall(self, user, call):
		""""""
		if not isinstance(call, Call):
			raise InvalidParameterError()
		if self.game is None:
			raise RequestUnavailableError()
		seat = self.getSeatForPlayer(user.name)
		if seat is None:  # User not playing.
			raise TablePlayingError()
		
		self.game.makeCall(seat, call)  # May raise a game error.
		
		self.informObservers('gameCallMade', seat=str(seat), call=call)
		# Check for contract or end of game.
		if self.game.bidding.isPassedOut():
			self.endGame()
		elif self.game.bidding.isComplete():
			contract = self.game.bidding.contract()
			for key in ['declarer', 'doubleBy', 'redoubleBy']:
				contract[key] = str(contract[key]) or None
			self.informObservers('gameContract', contract=contract)


	def view_playCard(self, user, card):
		"""Player in seat plays card."""
		if not isinstance(card, Card):
			raise InvalidParameterError()
		
		if self.game is None:
			raise RequestUnavailableError()
		seat = self.getSeatForPlayer(user.name)
		if seat is None:  # User not playing.
			raise TablePlayingError()
		
		# Declarer can play dummy's cards, dummy cannot play own cards.
		if self.game.whoseTurn() == self.game.playing.dummy:
			if seat == self.game.playing.declarer:
				seat = self.game.playing.dummy  # Declarer commands dummy.
			elif seat == self.game.playing.dummy:
				raise TablePlayingError()  # Dummy cannot play own cards.
		
		self.game.playCard(seat, card)  # May raise a game error.
		
		self.informObservers('gameCardPlayed', seat=str(seat), card=card)
		# Check for end of game.
		if self.game.isComplete():
			self.endGame()


	def view_whoseTurn(self, user):
		"""Return the seat that is next to play."""
		if self.game is None:
			raise RequestUnavailableError()
		return str(self.game.whoseTurn())


# Utility methods.


	def getSeatForPlayer(self, username):
		"""Returns seat of player username, or None."""
		for seat, player in self.players.items():
			if player == username:
				return seat
		return None


	def informObservers(self, eventName, **kwargs):
		"""For each observer, calls event handler with provided kwargs."""
		# Filter out observers with lost connections.
		for observer in self.observers.values():
			observer.callRemote(eventName, **kwargs)

