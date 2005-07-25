import os.path, gc, webbrowser
import gtk
from wrapper import WindowWrapper

from lib.core.enumeration import Rank, Seat, Suit
from lib.core.deck import Card, Deck


pixbufs_dir = "/usr/share/pixmaps/gnome-games-common/cards/"


class WindowMain(WindowWrapper):

	window_name = 'window_main'


	def new(self):
		# Load card mask into a pixbuf. We expect 13 x 5 unit cards.
		# Typical card mask size is 1028x615 pixels.
		card_mask_path = os.path.join(pixbufs_dir, "bonded.png")
		self.card_mask = gtk.gdk.pixbuf_new_from_file_at_size(card_mask_path, 1028, 615)
		self.card_width = self.card_mask.get_width() / 13
		self.card_height = self.card_mask.get_height() / 5
		self.hand_masks = dict.fromkeys(Seat.Seats, None)
		# Set up card table.
		self.card_table.set_size_request(width = 720, height = 540)
		self.card_table.connect("configure_event", self.configure_event)
		self.card_table.connect("expose_event", self.expose_event)
		self.card_table.connect("button_press_event", self.button_press_event)
		self.card_table.add_events(gtk.gdk.BUTTON_PRESS_MASK)
		bkg = gtk.gdk.pixbuf_new_from_file("/usr/share/pixmaps/cards/baize.png")
		self.background = bkg.render_pixmap_and_mask()[0]
		del bkg  # We won't need it any more.
		
		# TEMPORARY STUFF TO REMOVE LATER.
		d = Deck()
		d.shuffle()
		self.deck = d.deal()
		self.dummy = Seat.North


	def configure_event(self, widget, event):
		"""Creates backing pixmap of the appropriate size."""


		def draw_card(card, dest_pixbuf, pos_x, pos_y):
			"""Draw card to destination pixbuf at specified position."""
			# Index of each element corresponds to card image in card_mask.
			ranks = [Rank.Ace, Rank.Two, Rank.Three, Rank.Four, Rank.Five,
			         Rank.Six, Rank.Seven, Rank.Eight, Rank.Nine, Rank.Ten,
			         Rank.Jack, Rank.Queen, Rank.King]
			suits = [Suit.Club, Suit.Diamond, Suit.Heart, Suit.Spade]
			# Calculate co-ordinates of card in card_mask.
			if card.rank in ranks and card.suit in suits:
				src_x = ranks.index(card.rank) * self.card_width
				src_y = suits.index(card.suit) * self.card_height
			else:  # An unknown card is shown as the face down card.
				src_x, src_y = self.card_width * 2, self.card_height * 4
			self.card_mask.copy_area(src_x, src_y, self.card_width, self.card_height,
			                         dest_pixbuf, pos_x, pos_y)


		def build_cards_pixbuf(cards, spacing, wraparound, transpose=False, dummy=False):
			"""Returns a pixbuf of card images. Assumes cards are sorted by suit.

			spacing: (x,y) vector to offset cards.
			wraparound: number of cards to draw in row.
			transpose: if True, draw cards in columns.
			dummy: if True, wraparound for each suit. Ignores wraparound."""
			spacing_x, spacing_y = spacing
			if dummy:  # Calculate values for wraparound.
				wraparound = [0, 0, 0, 0]
				for card in cards:
					wraparound[Suit.Suits.index(card.suit)] += 1
			# Setup pixmap with appropriate dimensions.
			alpha, beta = max(wraparound)-1, len(wraparound)-1
			width = self.card_width + spacing_x*(transpose*beta + (not transpose)*alpha)
			height = self.card_height + spacing_y*(transpose*alpha + (not transpose)*beta)
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


		margin_x = margin_y = 16
		spacing = (self.card_width/2, self.card_height/4)
		
		x, y, width, height = widget.get_allocation()
		self.backing = gtk.gdk.Pixmap(widget.window, width, height)
		backgroundGC = gtk.gdk.GC(self.backing, fill=gtk.gdk.TILED, tile=self.background)
		self.backing.draw_rectangle(backgroundGC, True, 0, 0, width, height)

		rowfactors = {Seat.North : (13,), Seat.South : (13,), Seat.West : (4,3,3,3), Seat.East : (4,3,3,3)}
		coords = {Seat.North : lambda w, h: ((width-w)/2, margin_y),
		          Seat.South : lambda w, h: ((width-w)/2, height-h-margin_y),
		          Seat.East : lambda w, h: (width-w-margin_x, (height-h)/2),
		          Seat.West : lambda w, h: (margin_x, (height-h)/2)}

		for seat, hand in self.deck.items():
			# Render each hand mask separately.
			if not self.hand_masks[seat]:
				transpose, dummy = False, False
				self.hand_masks[seat] = build_cards_pixbuf(hand, spacing, rowfactors[seat], transpose, dummy)
			# Determine co-ordinates to draw hand mask on table.
			hand_width = self.hand_masks[seat][0].get_width()
			hand_height = self.hand_masks[seat][0].get_height()
			pos_x, pos_y = coords[seat](hand_width, hand_height)
			self.backing.draw_pixbuf(backgroundGC, self.hand_masks[seat][0], 0, 0, pos_x, pos_y)
			self.hand_masks[seat].append((pos_x, pos_y, pos_x+hand_width, pos_y+hand_height))
	
		gc.collect()  # Manual garbage collection. See PyGTK FAQ, section 8.4.
		return True   # Configure event is expected to return true.


	def expose_event(self, widget, event):
		"""Redraws widget from the backing pixmap."""
		x, y, width, height = event.area
		try:
			widget.window.draw_drawable(widget.get_style().bg_gc[gtk.STATE_NORMAL],
			                            self.backing, x, y, x, y, width, height)
		except AttributeError:
			pass
		return False  # Expose event is expected to return false.


	def button_press_event(self, widget, event):
		if event.button == 1 and self.backing != None:
			# Determine if button press event lies in a hand.
			for hand in self.hand_masks.values():
				start_x, start_y, finish_x, finish_y = hand[-1]
				if (start_x <= event.x <= finish_x) and (start_y <= event.y <= finish_y):
					pos_x, pos_y = event.x-start_x, event.y-start_y
					for card, x, y in hand[1][::-1]:  # Iterate backwards.
						if (x <= pos_x <= x+self.card_width) and (y <= pos_y <= y+self.card_height):
							status_context = self.statusbar_main.get_context_id("card")
							self.statusbar_main.push(status_context, str(card))
							return True
		return True  # Button press event is expected to return true.


	def server_connect(self):
		""" """
		pass


	def server_disconnect(self):
		""" """
		# if currently in game, ask.
		pass


	## START SIGNAL HANDLERS


	def on_window_main_destroy(self, widget, *args):
		gtk.main_quit()


	def on_quit_activate(self, widget, *args):
		print "Check exit confirmation from user."
		self.on_window_main_destroy(widget, *args)


	def on_toolbar_activate(self, widget, *args):
		if self.toolbar_main.get_property('visible'):
			self.toolbar_main.hide()
		else: self.toolbar_main.show()


	def on_statusbar_activate(self, widgets, *args):
		if self.statusbar_main.get_property('visible'):
			self.statusbar_main.hide()
		else: self.statusbar_main.show()


	def on_pybridge_home_activate(self, widget, *args):
		webbrowser.open('http://pybridge.sourceforge.net/')


	def on_about_activate(self, widget, *args):
		dialog_about = gtk.AboutDialog()
		dialog_about.set_name("PyBridge Client")
		dialog_about.set_version('0.0.1')
		dialog_about.set_copyright('Copyright 2004-2005 PyBridge Project')
		dialog_about.set_website('http://pybridge.sourceforge.net/')
		dialog_about.set_website_label('PyBridge Home')
		dialog_about.set_authors(['Michael Banks <michaelbanks@dsl.pipex.com>',
		                          'Sourav K Mandal <sourav@sourav.net>'])
		dialog_about.set_artists(['Stephen Banks <djbanksie@dsl.pipex.com>'])                  
		dialog_about.show()
		

	def on_serverconnect_activate(self, widget, *args):
		from dialog_serverconnect import DialogServerconnect
		dialog_serverconnect = DialogServerconnect()
