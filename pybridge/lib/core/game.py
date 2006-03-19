from deck import Card, Deck
from bidding import Call, Bidding
from play import Trick, Play


class GameError(Exception):
	pass


class Game:
	"""A game."""


	def __init__(self, dealer, deal, scoring, vulnNS, vulnEW):
		"""Initialises game.

		scoring: instance of scoring class.
		"""
		self.vulnNS, self.vulnEW = vulnNS, vulnEW
		self.contract = None
		self.deal = deal
		self.bidding, self.play, self.scoring = None, None, scoring
		self._startBidding(dealer)


	def isComplete(self):
		"""Returns True if game is complete, False otherwise."""
		if self.play:
			return self.play.isComplete()
		else:
			return self.bidding.isPassedOut()


	def makeCall(self, seat, call):
		"""Makes call from seat."""
		if self.bidding.isComplete():
			raise GameError("unavailable")

		if self.bidding.whoseTurn() is not seat:
			raise GameError("out of turn")
		elif not self.bidding.validCall(call):
			raise GameError("invalid call")

		self.bidding.addCall(call)
			

	def playCard(self, seat, card):
		"""Plays card from seat."""
		if not self.bidding.isComplete() or self.bidding.isPassedOut():
			raise GameError("unavailable")
		elif not self.play:
			self._startPlay()  # Kickstart play session.
		elif self.play.isComplete():
			raise GameError("unavailable")

		hand = self.deal[seat]
		if self.play.whoseTurn() is not seat:
			raise GameError("out of turn")
		elif not self.play.validCard(card, hand, seat):
			raise GameError("invalid card")
		
		self.play.playCard(card)


	def score(self):
		"""Returns the integer score value for declarer/dummy if:

		- bidding stage has been passed out, with no bids made.
		- play stage is complete.
		"""
		if not self.isComplete():
			raise GameError("unavailable")
		elif self.bidding.isPassedOut():
			return 0  # A passed out deal does not score.
		else:
			contract = self.bidding.contract()
			declarer, dummy = contract['declarer'], Seat.Seats[(Seat.Seats.index(contract['declarer']) + 2) % 4]
			vulnerable = (self.vulnNS and declarer in (Seat.North, Seat.South)) + (self.vulnEW and declarer in (Seat.West, Seat.East))
			
			result = {'contract'   : self.bidding.contract(),
			          'tricksMade' : self.play.wonTricks(declarer) + self.play.wonTricks(dummy),
			          'vulnerable' : vulnerable, }
			return self.scoring(result)


	def whoseTurn(self):
		"""Returns the seat that is next to call or play card."""
		if not self.bidding.isComplete():
			return self.bidding.whoseTurn()
		elif not self.play:
			self._startPlay()  # Kickstart play session.
		return self.play.whoseTurn()


	def _startBidding(self, dealer):
		self.bidding = Bidding(dealer)


	def _startPlay(self):
		contract  = self.bidding.contract()
		declarer  = contract['declarer']
		trumpSuit = contract['bidDenom']
		self.play = Play(declarer, trumpSuit)
