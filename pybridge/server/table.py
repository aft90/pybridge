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

from pybridge.common.call import Call
from pybridge.common.card import Card
from pybridge.common.deck import Deck
from pybridge.common.game import Game
from pybridge.common.scoring import scoreDuplicate

# Enumerations.
from pybridge.common.deck import Seat

from pybridge.failure import *

# Set up reconstruction of game objects from client.
pb.setUnjellyableForClass(Call, Call)
pb.setUnjellyableForClass(Card, Card)


class BridgeTable(pb.Viewable):
	"""A bridge table sits four players."""
	# TODO: perhaps subclass Table, facilitating tables for different card games.


	def __init__(self, name, server):
		self.name = name
		self.server = server
		
		# Set up bridge-related stuff.
		self.dealer    = Seat.North  # Rotate around the table for each deal.
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
		self.dealer = dealer or Seat[(self.dealer.index + 1) % 4]
		self.game = Game(self.dealer, deal, self.scoring, vulnNS=False, vulnEW=False)
		self.informObservers('gameStarted', dealer=str(self.dealer))


	def endGame(self):
		"""Called to terminate a game, when:
		
		- the bidding has been passed out without a contract.
		- the play has been completed.
		"""
		# TODO: get score.
		self.informObservers('gameEnded')
		self.game = None


# Remote methods.


	def view_getState(self, user):
		"""Produces information about the table."""
		players = {}  # Convert seat enumerations to strings.
		for seat, username in self.players.items():
			players[str(seat)] = username
		
		return {'players'   : players,
		        'observers' : self.observers.keys(),
		        'inGame'    : self.game != None, }


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
		
		# If all seats filled, and no game is currently running, start a game.
		if self.game is None and len([p for p in self.players.values() if p != None]) == 4:
			self.startGame()


	def view_standPlayer(self, user):
		"""Removes user from seat, provided user occupies seat."""
		seat = self.getSeatForPlayer(user.name)
		if seat is None:  # User not playing.
			raise TablePlayingError()
		
		self.players[seat] = None
		self.informObservers('playerStands', username=user.name, seat=str(seat))


	def view_getHand(self, user, seat):
		"""Returns the hand of player at seat, or DeniedRequest if hand is hidden.
		
		If user is a player, then their ability to view the hand will be examined.
		"""
		if seat not in Seat:
			raise InvalidParameterError()
		elif self.game is None:
			raise RequestUnavailableError()
		
		seat = getattr(Seat, seat)
		
		# If user is not a player, then userSeat == None.
		userSeat = self.getSeatForPlayer(user.name)
		
		if userSeat == None or userSeat == seat:
			return self.game.deal[seat]  # Player can see their own hand.
		if not self.game.bidding.isComplete():
			raise GameHandHiddenError()  # Bidding; no player can see another hand.
		
		dummy = Seat[(self.game.play.declarer.index + 2) % 4]
		if userSeat == dummy:
			return self.game.deal[seat]  # Play; dummy can see all hands.
		elif seat == dummy and len(self.game.play.tricks[0].cardsPlayed()) > 0:
			# Declarer and defenders can see dummy's hand after first card played.
			return self.game.deal[seat]
		else:
			raise GameHandHiddenError()


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
		
		self.informObservers('gameCallMade', seat=seat, call=call)
		# Check for contract or end of game.
		if self.game.bidding.isPassedOut():
			self.endGame()
		elif self.game.bidding.isComplete():
			contract = self.game.bidding.contract()
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
		
		self.game.playCard(seat, card)  # May raise a game error.
		
		self.informObservers('gameCardPlayed', seat=seat, card=card)
		# Check for end of game.
		if self.game.play.isComplete():
			self.endGame()


	def view_whoseTurn(self, user):
		"""Return the seat that is next to play."""
		if self.game is None:
			raise RequestUnavailableError()
		return self.game.whoseTurn()


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

