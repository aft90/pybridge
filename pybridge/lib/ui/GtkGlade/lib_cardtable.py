# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2005 PyBridge Project.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA


import gc, gtk, os.path

from lib.core.enumeration import Rank, Seat, Suit


# This library contains the code to render a card table.


# TODO: TEMPORARY CARD GENERATOR.
from lib.core.deck import Card, Deck
d = Deck()
deck = d.generateRandom()
dummy = Seat.North
# TODO TODO TODO TODO


pixbufs_dir = os.path.abspath('lib/graphics/')
background_path = os.path.join(pixbufs_dir, "baize.png")
card_mask_path = os.path.join(pixbufs_dir, "bonded.png")

background = gtk.gdk.pixbuf_new_from_file(background_path).render_pixmap_and_mask()[0]
card_mask = gtk.gdk.pixbuf_new_from_file_at_size(card_mask_path, 1028, 615)
card_width = card_mask.get_width() / 13
card_height = card_mask.get_height() / 5
hand_masks = dict.fromkeys(Seat.Seats, None)


def draw_card(card, dest_pixbuf, pos_x, pos_y):
	"""Draw card to destination pixbuf at specified position."""
	
	# Index of each element corresponds to card image in card_mask.
	ranks = [Rank.Ace, Rank.Two, Rank.Three, Rank.Four, Rank.Five,
	         Rank.Six, Rank.Seven, Rank.Eight, Rank.Nine, Rank.Ten,
	         Rank.Jack, Rank.Queen, Rank.King]
	suits = [Suit.Club, Suit.Diamond, Suit.Heart, Suit.Spade]
	# Calculate co-ordinates of card in card_mask.
	if card.rank in ranks and card.suit in suits:
		src_x = ranks.index(card.rank) * card_width
		src_y = suits.index(card.suit) * card_height
	else:  # An unknown card is shown as the face down card.
		src_x, src_y = card_width * 2, card_height * 4
	card_mask.copy_area(src_x, src_y, card_width, card_height, dest_pixbuf, pos_x, pos_y)


def build_cards_pixbuf(cards, spacing, wraparound, transpose=False, dummy=False):
	"""Returns a pixbuf of card images. Assumes cards are sorted by suit.
	
	spacing: (x,y) vector to offset cards.
	wraparound: number of cards to draw in row.
	transpose: if True, draw cards in columns.
	dummy: if True, wraparound for each suit. Ignores wraparound.
	"""
	
	spacing_x, spacing_y = spacing
	if dummy:  # Calculate values for wraparound.
		wraparound = [0, 0, 0, 0]
		for card in cards:
			wraparound[Suit.Suits.index(card.suit)] += 1
	# Setup pixmap with appropriate dimensions.
	alpha, beta = max(wraparound)-1, len(wraparound)-1
	width = card_width + spacing_x*(transpose*beta + (not transpose)*alpha)
	height = card_height + spacing_y*(transpose*alpha + (not transpose)*beta)
	cards_pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
	card_coords = []
	# Draw cards to pixmap.
	for index, card in [pair for pair in enumerate(cards) if pair!=None]:
		factor_y = 0
		while sum(wraparound[0:factor_y+1]) <= index:
			factor_y += 1
		factor_x = index - sum(wraparound[0:factor_y])
		pos_x = spacing_x * (transpose*factor_y + (not transpose)*factor_x)
		pos_y = spacing_y * (transpose*factor_x + (not transpose)*factor_y)
		draw_card(card, cards_pixbuf, pos_x, pos_y)
		card_coords.append((card, pos_x, pos_y))
	return [cards_pixbuf, card_coords]


def configure_event(widget, event):
	"""Creates backing pixmap of the appropriate size."""

	global backing  # Preserve backing object.
	margin_x = margin_y = 16
	spacing = (card_width/2, card_height/4)
	
	x, y, width, height = widget.get_allocation()
	backing = gtk.gdk.Pixmap(widget.window, width, height)
	backgroundGC = gtk.gdk.GC(backing, fill=gtk.gdk.TILED, tile=background)
	backing.draw_rectangle(backgroundGC, True, 0, 0, width, height)
	rowfactors = {Seat.North : (13,), Seat.South : (13,), Seat.West : (4,3,3,3), Seat.East : (4,3,3,3)}
	coords = {Seat.North : lambda w, h: ((width-w)/2, margin_y),
	          Seat.South : lambda w, h: ((width-w)/2, height-h-margin_y),
	          Seat.East : lambda w, h: (width-w-margin_x, (height-h)/2),
	          Seat.West : lambda w, h: (margin_x, (height-h)/2)}
	for seat, hand in deck.items():
		# Render each hand mask separately.
		if not hand_masks[seat]:
			transpose, dummy = False, False
			hand_masks[seat] = build_cards_pixbuf(hand, spacing, rowfactors[seat], transpose, dummy)
		# Determine co-ordinates to draw hand mask on table.
		hand_width = hand_masks[seat][0].get_width()
		hand_height = hand_masks[seat][0].get_height()
		pos_x, pos_y = coords[seat](hand_width, hand_height)
		backing.draw_pixbuf(backgroundGC, hand_masks[seat][0], 0, 0, pos_x, pos_y)
		hand_masks[seat].append((pos_x, pos_y, pos_x+hand_width, pos_y+hand_height))

	gc.collect()  # Manual garbage collection. See PyGTK FAQ, section 8.4.
	return True   # Configure event is expected to return true.


def expose_event(widget, event):
	"""Redraws widget from the backing pixmap."""

	x, y, width, height = event.area
	widget.window.draw_drawable(widget.get_style().bg_gc[gtk.STATE_NORMAL], backing, x, y, x, y, width, height)
	return False  # Expose event is expected to return false.


def button_press_event(widget, event):

	if event.button == 1 and backing != None:
		# Determine if button press event lies in a hand.
		for hand in hand_masks.values():
			start_x, start_y, finish_x, finish_y = hand[-1]
			if (start_x <= event.x <= finish_x) and (start_y <= event.y <= finish_y):
				pos_x, pos_y = event.x-start_x, event.y-start_y
				for card, x, y in hand[1][::-1]:  # Iterate backwards.
					if (x <= pos_x <= x+card_width) and (y <= pos_y <= y+card_height):
#						status_context = statusbar_main.get_context_id("card")
#						statusbar_main.push(status_context, str(card))
						return True
	return True  # Button press event is expected to return true.
