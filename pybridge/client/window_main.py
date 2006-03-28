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

from wrapper import GladeWrapper

from connector import connector
from windowmanager import windowmanager
from pybridge.conf import PYBRIDGE_VERSION
from pybridge.common.enumeration import Rank, Seat, Suit
from pybridge.environment import environment

BACKGROUND_PATH = environment.find_pixmap("baize.png")
CARD_MASK_PATH = environment.find_pixmap("bonded.png")

CARD_MASK_RANKS = [Rank.Ace, Rank.Two, Rank.Three, Rank.Four, Rank.Five,
                   Rank.Six, Rank.Seven, Rank.Eight, Rank.Nine, Rank.Ten,
                   Rank.Jack, Rank.Queen, Rank.King]

CARD_MASK_SUITS = [Suit.Club, Suit.Diamond, Suit.Heart, Suit.Spade]

COORDS = {
	Seat.North : lambda w, h: ((width-w)/2, margin_y),
	Seat.South : lambda w, h: ((width-w)/2, height-h-margin_y),
	Seat.East  : lambda w, h: (width-w-margin_x, (height-h)/2),
	Seat.West  : lambda w, h: (margin_x, (height-h)/2),
}

WRAPAROUNDS = {
	Seat.North : (13,),
	Seat.South : (13,),
	Seat.East  : (4, 3, 3, 3),
	Seat.West  : (4, 3, 3, 3),
}


class WindowMain(GladeWrapper):

	glade_name = 'window_main'


	def new(self):
		# Placeholders for pixbuf representations of active observed table.
		self.backing = None
		self.hand_masks = dict.fromkeys(Seat.Seats, None)
		
		# Load table background and card pixbufs.
		self.background = gtk.gdk.pixbuf_new_from_file(BACKGROUND_PATH).render_pixmap_and_mask()[0]
		self.card_mask = gtk.gdk.pixbuf_new_from_file_at_size(CARD_MASK_PATH, 1028, 615)
		# Expect cards of unit size 13 x 5.
		self.card_width = self.card_mask.get_width() / 13
		self.card_height = self.card_mask.get_height() / 5
		
		self.card_table.set_size_request(width=640, height=480)
		self.card_table.connect("configure_event", self.card_table_configure)
		self.card_table.connect("expose_event", self.card_table_expose)
		self.card_table.connect("button_press_event", self.card_table_button_press)
		self.card_table.add_events(gtk.gdk.BUTTON_PRESS_MASK)
		
		windowmanager.launch('window_tablelisting')

#		# Set up table and user listings.
#		cell_renderer = gtk.CellRendererText()
#		self.table_store = gtk.ListStore(str)
#		self.table_listing.set_model(self.table_store)
#		for index, title in enumerate(('Table Name', )):
#			column = gtk.TreeViewColumn(title, cell_renderer, text=index)
#			self.table_listing.append_column(column)
#		self.user_store = gtk.ListStore(str)
#		self.user_listing.set_model(self.user_store)
#		for index, title in enumerate(('User Name', )):
#			column = gtk.TreeViewColumn(title, cell_renderer, text=index)
#			self.user_listing.append_column(column)




#	def user_online(self, username):
#		"""Adds a user to the user listing."""
#		row = (username, )
#		iter = self.user_store.append(row)
#		self.users_online[username] = iter
#
#
#	def user_offline(self, username):
#		"""Removes a user from the user listing."""
#		iter = self.users_online[username]
#		self.user_store.remove(iter)
#		del self.users_online[username]


# The following code drives the card tables.


	def draw_card(self, dest_pixbuf, pos_x, pos_y, card=None):
		"""Draws graphic of specified card to dest_pixbuf at (pos_x, pos_y)."""
		if card:  # Determine co-ordinates of card graphic in card_mask pixbuf.
			src_x = CARD_MASK_RANKS.index(card.rank) * self.card_width
			src_y = CARD_MASK_SUITS.index(card.suit) * self.card_height
		else:  # If no card is specified, draw a face-down card.
			src_x, src_y = self.card_width*2, self.card_height*4
		self.card_mask.copy_area(src_x, src_y, self.card_width, self.card_height, dest_pixbuf, pos_x, pos_y)


	def build_hand_pixbuf(self, cards, space_x, space_y, wraparound=None, transpose=False, dummy=False):
		"""Returns a pixbuf of card images. Assumes cards are sorted by suit.
	
		cards: list of card objects and None objects to be drawn.
		space_x: horizontal offset between cards in each row.
		space_y: vertical offset between rows.
		wraparound: tuple of integers, where index of integer = row number
		            and integer = number of cards to draw in row.
		transpose: if True, draw cards in columns, otherwise, draw cards in rows.
		
		If wraparound is omitted or dummy is True, cards will be drawn in rows of suits.
		"""

		# If required, calculate the row offsets.
		if wraparound is None or dummy is True:
			wraparound = [0, 0, 0, 0]
			for card in cards:
				wraparound[Suit.Suits.index(card.suit)] += 1

		# Setup pixmap with appropriate dimensions.
		alpha, beta = max(wraparound)-1, len(wraparound)-1
		width = card_width + spacing_x*(transpose*beta + (not transpose)*alpha)
		height = card_height + spacing_y*(transpose*alpha + (not transpose)*beta)
		cards_pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)

		# Draw cards to pixmap.
		card_coords = []
		for index, card in [pair for pair in enumerate(cards)]: #if pair!=None]:
			factor_y = 0
			while sum(wraparound[0:factor_y+1]) <= index:
				factor_y += 1
			factor_x = index - sum(wraparound[0:factor_y])
			pos_x = spacing_x * (transpose*factor_y + (not transpose)*factor_x)
			pos_y = spacing_y * (transpose*factor_x + (not transpose)*factor_y)
			draw_card(cards_pixbuf, pos_x, pos_y, card)
			card_coords.append((card, pos_x, pos_y))

		return cards_pixbuf, card_coords


	def card_table_configure(self, widget, event):
		"""Creates backing pixmap of the appropriate size."""
		x, y, width, height = widget.get_allocation()
		self.backing = gtk.gdk.Pixmap(self.card_table.window, width, height)
		backgroundGC = gtk.gdk.GC(self.backing, fill=gtk.gdk.TILED, tile=self.background)
		self.backing.draw_rectangle(backgroundGC, True, 0, 0, width, height)

#		for seat, hand in deck.items():
#			# Render each hand mask separately.
#			if not hand_masks[seat]:
#				#transpose, dummy = False, False
##				hand_masks[seat] = build_cards_pixbuf(hand, 16, 16, WRAPAROUNDS[seat])
#			# Determine co-ordinates to draw hand mask on table.
#			hand_width = hand_masks[seat][0].get_width()
#			hand_height = hand_masks[seat][0].get_height()
#			pos_x, pos_y = coords[seat](hand_width, hand_height)
#			backing.draw_pixbuf(backgroundGC, hand_masks[seat][0], 0, 0, pos_x, pos_y)
#			hand_masks[seat].append((pos_x, pos_y, pos_x+hand_width, pos_y+hand_height))

		# Save hand masks and card coords.
		pass

		gc.collect()  # Manual garbage collection. See PyGTK FAQ, section 8.4.
		return True   # Configure event is expected to return true.


	def card_table_expose(self, widget, event):
		"""Redraws card table widget from the backing pixmap."""
		x, y, width, height = event.area
		widget.window.draw_drawable(widget.get_style().bg_gc[gtk.STATE_NORMAL],
		                            self.backing, x, y, x, y, width, height)
		return False  # Expose event is expected to return false.


	def card_table_button_press(self, widget, event):
		""""""

		if event.button == 1 and self.backing != None:
			# Determine if button press event lies in a hand.
			for hand in hand_masks.values():
				start_x, start_y, finish_x, finish_y = hand[-1]
				if (start_x <= event.x <= finish_x) and (start_y <= event.y <= finish_y):
					pos_x, pos_y = event.x-start_x, event.y-start_y
					for card, x, y in hand[1][::-1]:  # Iterate backwards.
						if (x <= pos_x <= x+card_width) and (y <= pos_y <= y+card_height):
#							status_context = statusbar_main.get_context_id("card")
#							statusbar_main.push(status_context, str(card))
							return True
		return True  # Button press event is expected to return true.


	# Signal handlers


	def on_window_main_delete_event(self, widget, *args):
		windowmanager.shutdown()


	def on_hosttable_activate(self, widget, *args):
		windowmanager.launch('dialog_newtable')


	def on_tablelisting_toggled(self, widget, *args):
		window = windowmanager.get('window_tablelisting').window
		if self.button_tablelisting.get_active():
			window.show()
		else:
			window.hide()


	def on_disconnect_activate(self, widget, *args):
		connector.disconnect()
		windowmanager.terminate('window_main')
		windowmanager.launch('dialog_connection')


	def on_quit_activate(self, widget, *args):
		windowmanager.shutdown()


	def on_about_activate(self, widget, *args):
		about = gtk.AboutDialog()
		about.set_name('PyBridge')
		about.set_version(PYBRIDGE_VERSION)
		about.set_copyright('Copyright (C) 2004-2006 Michael Banks')
		about.set_comments('Online bridge made easy')
		about.set_website('http://sourceforge.net/projects/pybridge/')
		license = file(environment.find_doc('COPYING')).read()
		about.set_license(license)
		authorsfile = file(environment.find_doc('AUTHORS'))
		authors = [author.strip() for author in authorsfile.readlines()]
		about.set_authors(authors)
		logo_path = environment.find_pixmap('pybridge.png')
		logo = gtk.gdk.pixbuf_new_from_file(logo_path)
		about.set_logo(logo)
		
		about.run()
		about.destroy()
