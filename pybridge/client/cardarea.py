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


import gc, gtk

from pybridge.environment import environment

BACKGROUND_PATH = environment.find_pixmap("baize.png")
CARD_MASK_PATH = environment.find_pixmap("bonded.png")

from pybridge.common.card import Card, Rank, Suit
from pybridge.common.deck import Seat

CARD_MASK_RANKS = [Rank.Ace, Rank.Two, Rank.Three, Rank.Four, Rank.Five,
                   Rank.Six, Rank.Seven, Rank.Eight, Rank.Nine, Rank.Ten,
                   Rank.Jack, Rank.Queen, Rank.King]

CARD_MASK_SUITS = [Suit.Club, Suit.Diamond, Suit.Heart, Suit.Spade]

BORDER_X = BORDER_Y = 8

WRAPAROUNDS = {Seat.North : (13,), Seat.East : (4, 3, 3, 3),
               Seat.South : (13,), Seat.West : (4, 3, 3, 3), }


class CardArea(gtk.DrawingArea):

	# TODO: when PyGTK 2.8 becomes widespread, adapt this module to Cairo.


	def __init__(self):
		gtk.DrawingArea.__init__(self)
		
		self.backing = None     # Placeholder for backing pixbuf.
		self.hand_pixbufs = {}  # Hand pixbufs, keyed by seat.
		self.hand_coords = {}   # Positions of hand pixbufs on backing.
		self.card_coords = {}   # Positions of cards on hand pixbufs.
		self.trick_pixbuf = None  # 
		
		# Load table background and card pixbufs.
		self.background = gtk.gdk.pixbuf_new_from_file(BACKGROUND_PATH).render_pixmap_and_mask()[0]
		self.card_mask = gtk.gdk.pixbuf_new_from_file_at_size(CARD_MASK_PATH, 1028, 615)
		
		# Expect cards of unit size 13 x 5.
		self.card_width = self.card_mask.get_width() / 13
		self.card_height = self.card_mask.get_height() / 5
		self.spacing_x = int(self.card_width * 0.4)
		self.spacing_y = int(self.card_height * 0.2)
		
		# Method to call when a card is clicked.
		self.on_card_clicked = None
		
		# Set up events.
		self.connect('configure_event', self.configure)
		self.connect('expose_event', self.expose)
		self.connect('button_press_event', self.button_press)
		self.add_events(gtk.gdk.BUTTON_PRESS_MASK)


	def draw_card(self, dest_pixbuf, pos_x, pos_y, card):
		"""Draws graphic of specified card to dest_pixbuf at (pos_x, pos_y)."""
		if isinstance(card, Card):  # Determine coordinates of graphic in card_mask.
			src_x = CARD_MASK_RANKS.index(card.rank) * self.card_width
			src_y = CARD_MASK_SUITS.index(card.suit) * self.card_height
		else:  # Draw a face-down card.
			src_x, src_y = self.card_width*2, self.card_height*4
		
		self.card_mask.copy_area(src_x, src_y, self.card_width, self.card_height,
		                         dest_pixbuf, pos_x, pos_y)


	def build_hand(self, seat, hand, transpose=False, dummy=False):
		"""Builds and saves a pixbuf of card images. Assumes cards are sorted by suit.
	
		hand: list of card objects and None objects to be drawn.
		transpose: if True, draw cards in columns, otherwise, draw cards in rows.
		dummy: if True, draw cards in rows of suits.
		"""
		
		# Sort hand, according to the high->low red-black-red-black convention.
		
		
		# The wraparound is a tuple of integers, where, for each integer:
		# - index of integer in tuple = row number
		# - integer = number of cards to draw in row.
		
		if dummy:  # If required, calculate the row offsets.
			wraparound = [0, 0, 0, 0]
			for card in hand:
				wraparound[card.suit.index] += 1
		else:
			wraparound = WRAPAROUNDS[seat]
		
		# Setup hand pixbuf with appropriate dimensions.
		alpha, beta = max(wraparound)-1, len(wraparound)-1
		width = self.card_width + self.spacing_x*(transpose*beta + (not transpose)*alpha)
		height = self.card_height + self.spacing_y*(transpose*alpha + (not transpose)*beta)
		self.hand_pixbufs[seat] = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
#		self.hand_pixbufs[seat].fill(0x00000000)  # Clear pixbuf.

		# Draw cards to hand pixbuf.
		self.card_coords[seat] = []
		for index, card in enumerate(hand):
			if card is not None:  # None represents a space.
				factor_y = 0
				while sum(wraparound[0:factor_y+1]) <= index:
					factor_y += 1
				factor_x = index - sum(wraparound[0:factor_y])
				pos_x = self.spacing_x * (transpose*factor_y + (not transpose)*factor_x)
				pos_y = self.spacing_y * (transpose*factor_x + (not transpose)*factor_y)
				self.draw_card(self.hand_pixbufs[seat], pos_x, pos_y, card)
				self.card_coords[seat].append((card, pos_x, pos_y))


	def draw_hand(self, seat):
		""""""
		x, y, width, height = self.get_allocation()
		
		# When called with (w, h) of hand pixbuf, returns (x, y) start point to draw hand.
		coords = {Seat.North : lambda w, h: ((width-w)/2, BORDER_Y),
		          Seat.East  : lambda w, h: (width-w-BORDER_X, (height-h)/2),
		          Seat.South : lambda w, h: ((width-w)/2, height-h-BORDER_Y),
		          Seat.West  : lambda w, h: (BORDER_X, (height-h)/2), }
		
		# Determine coordinates in backing pixmap to draw hand pixbuf.
		hand_pixbuf = self.hand_pixbufs[seat]
		hand_width = hand_pixbuf.get_width()
		hand_height = hand_pixbuf.get_height()
		pos_x, pos_y = coords[seat](hand_width, hand_height)
		
		# Draw hand pixbuf and save hand coordinates.
		self.backing.draw_rectangle(self.backingGC, True, pos_x, pos_y, hand_width, hand_height)
		self.backing.draw_pixbuf(self.backingGC, hand_pixbuf, 0, 0, pos_x, pos_y)
		self.hand_coords[seat] = (pos_x, pos_y, pos_x+hand_width, pos_y+hand_height)
		
		# Redraw modified area of backing pixbuf.
		self.window.invalidate_rect((pos_x, pos_y, hand_width, hand_height), False)


	def build_trick(self, trick):
		"""Builds and saves a pixbuf of trick."""
		width = self.card_width + self.spacing_x*2
		height = self.card_height + self.spacing_y*2
		self.trick_pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
		self.trick_pixbuf.fill(0x00000000)  # Clear pixbuf.

		# When called, returns (x, y) start point to draw card.
		coords = {Seat.North : lambda: ((width-self.card_width)/2, 0),
		          Seat.East  : lambda: (width-self.card_width, (height-self.card_height)/2),
		          Seat.South : lambda: ((width-self.card_width)/2, height-self.card_height),
		          Seat.West  : lambda: (0, (height-self.card_height)/2), }
		
		# Draw cards in order of play, to permit overlapping of cards.
		leader, cards = trick
		seatorder = Seat[leader.index:] + Seat[:leader.index]
		for seat in [s for s in seatorder if s in cards]:
			pos_x, pos_y = coords[seat]()
			self.draw_card(self.trick_pixbuf, pos_x, pos_y, cards[seat])


	def draw_trick(self):
		""""""
		x, y, width, height = self.get_allocation()
		
		trick_width = self.trick_pixbuf.get_width()
		trick_height = self.trick_pixbuf.get_height()
		pos_x = (width - trick_width) / 2
		pos_y = (height - trick_height) / 2
		self.backing.draw_rectangle(self.backingGC, True, pos_x, pos_y, trick_width, trick_height)
		self.backing.draw_pixbuf(self.backingGC, self.trick_pixbuf, 0, 0, pos_x, pos_y)
		
		# Redraw modified area of backing pixbuf.
		rect = (pos_x, pos_y, trick_width, trick_height)
		self.window.invalidate_rect(rect, False)


	def configure(self, widget, event):
		"""Creates backing pixmap of the appropriate size, containing hand pixbufs."""
		x, y, width, height = widget.get_allocation()
		self.backing = gtk.gdk.Pixmap(widget.window, width, height)
		self.backingGC = gtk.gdk.GC(self.backing, fill=gtk.gdk.TILED, tile=self.background)
		self.backing.draw_rectangle(self.backingGC, True, 0, 0, width, height)
		
		for seat in self.hand_pixbufs:
			self.draw_hand(seat)
		if self.trick_pixbuf:
			self.draw_trick()

		gc.collect()  # Manual garbage collection. See PyGTK FAQ, section 8.4.
		return True   # Configure event is expected to return true.


	def expose(self, widget, event):
		"""Redraws card table widget from the backing pixmap."""
		x, y, width, height = event.area
		widget.window.draw_drawable(widget.get_style().bg_gc[gtk.STATE_NORMAL],
		                            self.backing, x, y, x, y, width, height)
		return False  # Expose event is expected to return false.


	def button_press(self, widget, event):
		"""Determines which card was clicked, then calls external handler method."""
		
		def get_hand_xy():
			for seat, hand in self.hand_coords.items():
				start_x, start_y, finish_x, finish_y = hand
				if (start_x <= event.x <= finish_x) and (start_y <= event.y <= finish_y):
					return seat, start_x, start_y
		
		def get_card_in_hand(seat, start_x, start_y):
			pos_x = event.x - start_x
			pos_y = event.y - start_y
			for card, x, y in self.card_coords[seat][::-1]:  # Iterate backwards.
				if (x <= pos_x <= x+self.card_width) and (y <= pos_y <= y+self.card_height):
					return card
		
		if event.button == 1 and self.on_card_clicked:
			hand_xy = get_hand_xy()
			if hand_xy:
				card = get_card_in_hand(*hand_xy)
				if card is not None:
					self.on_card_clicked(card)  # External handler.
		
		return True  # Button press event is expected to return true.

