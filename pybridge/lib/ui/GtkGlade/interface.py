import os, sys, gc
import gtk
from wrapper import WindowWrapper

from lib.core.enumeration import Rank, Seat, Suit
from lib.core.deck import Card, Deck

#import dialog_about, window_bidding

pixbufs_dir = "/usr/share/pixmaps/gnome-games-common/cards/"

class WindowMain(WindowWrapper):

	window_name = 'window_main'

	def new(self):
		
		# Initialise child windows and dialogs.
		self.window_bidbox = WindowBidbox()
		self.window_bidding = WindowBidding()
		self.window_rooms = WindowRooms()
		self.dialog_about = DialogAbout()
		self.dialog_serverconnect = DialogServerconnect()
		
		# Load card mask into a pixbuf. We expect 13 x 5 unit cards.
		card_mask_path = os.path.join(pixbufs_dir, "paris.svg")
		self.card_mask = gtk.gdk.pixbuf_new_from_file(card_mask_path)
		self.card_width = self.card_mask.get_width() / 13
		self.card_height = self.card_mask.get_height() / 5
		
		# Set up card table.
		self.deck = Deck()   # temp
		self.deck.shuffle()  # temp
		self.deck.deal()     # temp
		self.hand_masks = dict.fromkeys(Seat.Seats, None)
		self.card_table.set_size_request(width = 720, height = 540)
		self.card_table.connect("configure_event", self.configure_event)
		self.card_table.connect("expose_event", self.expose_event)
		self.card_table.connect("button_press_event", self.button_press_event)
		self.card_table.add_events(gtk.gdk.BUTTON_PRESS_MASK)
		
		# Set up card table background.
		background_color = gtk.gdk.color_parse("#376014")
		self.card_table.modify_bg(gtk.STATE_NORMAL, background_color)


	def configure_event(self, widget, event):
		"""Creates backing pixmap of the appropriate size."""


		def draw_card(widget, card, pos_x, pos_y):
			"""Draw card image to widget at specified position."""

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
			widget.draw_pixbuf(None, self.card_mask,
			                   src_x, src_y, pos_x, pos_y,
			                   self.card_width, self.card_height)


		def build_cards_pixmap(cards, spacing, wibble, dummy=0):
			"""Return a pixmap of card images.

			spacing: (x,y) vector to offset cards.
			wibble: 
			dummy: """
			
			spacing_x, spacing_y = spacing

			if dummy:
				# Split the cards into suits.
				suit_split = {Suit.Club : [], Suit.Diamond : [], Suit.Heart : [], Suit.Spade : []}
				for card in cards:
					suit_split[card.suit].append(card)
				# We need to know the longest suit.
				maxlength = max([len(suit) for suit in suit_split.values()])

				#if dummy == 1:
				#	width = self.card_width + 3*spacing_x
				#	height = self.card_height + (maxlength-1)*spacing_y
				#else:
				width = self.card_width + (maxlength-1)*spacing_x
				height = self.card_height + 3*spacing_y
					
				# Setup pixmap with appropriate dimensions.
				cards_pixmap = gtk.gdk.Pixmap(self.card_table.window, width, height)
				cards_pixmap.draw_rectangle(self.card_table.get_style().bg_gc[gtk.STATE_NORMAL],
				                            True, 0, 0, width, height)

				for factor_y, suit in enumerate(Suit.Suits):
					pos_y = factor_y * spacing_y
					for factor_x, card in enumerate(suit_split[suit]):
						pos_x = factor_x * spacing_x
						#if dummy == 1: pos_x, pos_y = pos_y, pos_x
						draw_card(cards_pixmap, card, pos_x, pos_y)

			else:
				# Setup pixmap with appropriate dimensions.
				width = self.card_width + (wibble-1)*spacing_x
				height = self.card_height + ((13/wibble + (13%wibble>0))-1)*spacing_y  # Crude rounding. Fix.
				cards_pixmap = gtk.gdk.Pixmap(self.card_table.window, width, height)
				cards_pixmap.draw_rectangle(self.card_table.get_style().bg_gc[gtk.STATE_NORMAL],
				                            True, 0, 0, width, height)
				for index, card in [pair for pair in enumerate(cards) if pair!=None]:
					factor_x = index % wibble  # index mod wibble
					factor_y = index / wibble  # floor(index div wibble)
					pos_x = spacing_x * (index % wibble)
					pos_y = spacing_y * (index / wibble)
					draw_card(cards_pixmap, card, pos_x, pos_y)
			return cards_pixmap


		margin_x = margin_y = 16
		spacing = (self.card_width/2, self.card_height/4)
		
		x, y, width, height = widget.get_allocation()
		self.backing = gtk.gdk.Pixmap(widget.window, width, height)
		self.backing.draw_rectangle(widget.get_style().bg_gc[gtk.STATE_NORMAL],
		                            True, 0, 0, width, height)

		coords = {Seat.North : lambda w, h: ((width-w)/2, margin_y),
		          Seat.South : lambda w, h: ((width-w)/2, height-h-margin_y),
		          Seat.East : lambda w, h: (width-w-margin_x, (height-h)/2),
		          Seat.West : lambda w, h: (margin_x, (height-h)/2)}

		self.card_coords = []
		self.hand_coords = []
		rowfactors = {Seat.North : 13, Seat.South : 13, Seat.West : 4, Seat.East : 4}

		for seat, hand in self.deck.hands.items():
			# Render each hand separately.
			if not self.hand_masks[seat]:
				# We need to create and store the hand mask.
				hand.sort()
				self.hand_masks[seat] = build_cards_pixmap(hand.cards, spacing, rowfactors[seat], seat==Seat.North)
			# Now determine coords on table.
			hand_width, hand_height = self.hand_masks[seat].get_size()
			pos_x, pos_y = coords[seat](hand_width, hand_height)
			self.hand_coords.append(((pos_x, pos_y), (pos_x+hand_width, pos_y+hand_height)))
			self.backing.draw_drawable(self.card_table.get_style().bg_gc[gtk.STATE_NORMAL],
			                           self.hand_masks[seat], 0, 0, pos_x, pos_y, -1, -1)
	
		gc.collect()  # Manual garbage collection. PyGTK FAQ, section 8.4.
		return True  # Configure event is expected to return true.


	def expose_event(self, widget, event):
		""" Redraws the screen from the backing pixmap. """

		x, y, width, height = event.area
		widget.window.draw_drawable(widget.get_style().bg_gc[gtk.STATE_NORMAL],
		                            self.backing, x, y, x, y, width, height)
		return False  # Expose event is expected to return false.


	def button_press_event(self, widget, event):

		if event.button == 1 and self.backing != None:
			# Iterate over co-ordinates backwards, as items at back of list
			# may be drawn over items at front of list.
			for hand, (hand_start, hand_finish) in self.hand_coords[::-1]:
				if (hand_start[0] <= event.x <= hand_finish[0]) and \
				   (hand_start[1] <= event.y <= hand_finish[1]):
					for card in self.hands[hand].cards[::-1]:
						# Note that we are working from separate lists here.
						card_start, card_finish = self.card_coords[card]
						if (card_start[0] <= event.x <= card_finish[0]) and \
						   (card_start[1] <= event.y <= card_finish[1]):
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
		# Must check that we can quit here.
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
		import webbrowser
		webbrowser.open('http://pybridge.sourceforge.net/')


	def on_about_activate(self, widget, *args):
		self.dialog_about.window.show()


	def on_serverconnect_activate(self, widget, *args):
		self.dialog_serverconnect.window.show()


class WindowBidding(WindowWrapper):

	window_name = 'window_bidding'


	def new(self):
		self.call_tree_model = gtk.TreeStore(str, str, str, str)
		self.call_tree.set_model(self.call_tree_model)
		self.model_iter = self.call_tree_model.insert_after(parent = None, sibling = None)
		self.column = 0
		columnNames = ['North', 'East', 'South', 'West']
		i = 0
		for columnName in columnNames:
			renderer = gtk.CellRendererText()
			column = gtk.TreeViewColumn(columnName, renderer, text = i)
			self.call_tree.append_column(column)
			i+=1
		for x in range(23):
			self.insert_cell(x)


	def insert_cell(self, data):
		if self.column == 4:
			self.column = 0
			self.model_iter = self.call_tree_model.insert_after(parent = None, sibling = self.model_iter)
		self.call_tree_model.set_value(self.model_iter, self.column, value = data)
		self.column += 1


class WindowBidbox(WindowWrapper):

	window_name = 'window_bidbox'


class WindowRooms(WindowWrapper):

	window_name = 'window_rooms'

	def new(self):
		self.room_tree_model = gtk.TreeStore(str, str, str)
		self.room_tree.set_model(self.room_tree_model)
		self.model_iter = self.room_tree_model.insert_after(parent = None, sibling = None)


class DialogAbout(WindowWrapper):

	window_name = 'dialog_about'

	def new(self):
		self.dialog_about.set_name('PyBridge Client')
		self.dialog_about.set_version('0.0.1')
		self.dialog_about.set_copyright('Copyright 2004-2005 Michael Banks, Sourav K Mandal')
		self.dialog_about.set_website('http://pybridge.sourceforge.net/')
		self.dialog_about.set_website_label('PyBridge Home')
		self.dialog_about.set_authors(['Michael Banks <michaelbanks@dsl.pipex.com>', 'Sourav K Mandal <sourav@sourav.net>'])
		self.dialog_about.set_artists(['Stephen Banks <djbanksie@dsl.pipex.com>'])


class DialogServerconnect(WindowWrapper):
	window_name = 'dialog_serverconnect'

	def new(self):
		pass
