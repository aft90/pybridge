import os, sys, gc
import gtk

from lib.core.enumeration import Rank, Seat, Suit
from lib.core.deck import Card, Deck

from wrapper import WindowWrapper

pixmaps_dir = "/usr/share/pixmaps/gnome-games-common/cards/"

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
		card_mask_path = os.path.join(pixmaps_dir, "paris.svg")
		self.card_mask = gtk.gdk.pixbuf_new_from_file(card_mask_path)
		# Set up card table.
	
		# TEMP
		self.deck = Deck()
		self.deck.shuffle()
		self.deck.deal()

		self.card_table.set_size_request(width = 720, height = 560)
		self.card_table.connect("configure_event", self.configure_event)
		self.card_table.connect("expose_event", self.expose_event)
		# Set up card table background.
		background_color = gtk.gdk.color_parse("#376014")
		self.card_table.modify_bg(gtk.STATE_NORMAL, background_color)

	def configure_event(self, widget, event):
		"""Creates backing pixmap of the appropriate size."""
		x, y, width, height = widget.get_allocation()
		self.backing = gtk.gdk.Pixmap(widget.window, width, height)
		self.backing.draw_rectangle(widget.get_style().bg_gc[gtk.STATE_NORMAL],
		                            True, 0, 0, width, height)
		self.draw_table(self.backing)
		# Manual garbage collection. See the PyGTK FAQ, section 8.4.
		gc.collect()
		# A configure event is expected to return true.
		return True

	def expose_event(self, widget, event):
		""" Redraws the screen from the backing pixmap. """
		x, y, width, height = event.area
		widget.window.draw_drawable(widget.get_style().bg_gc[gtk.STATE_NORMAL],
		                            self.backing, x, y, x, y, width, height)
		# An expose event is expect to return false.
		return False
	
	def draw_card(self, widget, card, pos_x, pos_y):
		"""Draws a single card to widget at specified position."""
		# The elements of these lists correspond to card images in pixbuf.
		ranks = [Rank.Ace, Rank.Two, Rank.Three, Rank.Four, Rank.Five,
		         Rank.Six, Rank.Seven, Rank.Eight, Rank.Nine, Rank.Ten,
		         Rank.Jack, Rank.Queen, Rank.King]
		suits = [Suit.Club, Suit.Diamond, Suit.Heart, Suit.Spade]
		# Get card dimensions from pixbuf.
		card_width = self.card_mask.get_width() / 13
		card_height = self.card_mask.get_height() / 5
		# Calculate co-ordinates of card in mask pixbuf.
		if card.rank in ranks and card.suit in suits:
			src_x = ranks.index(card.rank) * card_width
			src_y = suits.index(card.suit) * card_height
		else:
			# An unknown card is shown as the face down card.
			src_x, src_y = card_width * 2, card_height * 4
		widget.draw_pixbuf(None, self.card_mask, src_x, src_y, pos_x, pos_y,
		                   card_width, card_height)

	def draw_cards(self, widget, cards, start, spacing, factor, dummy=False):
		"""Draw a sequence of cards to widget."""
		if dummy:
			# Dummy Mode. No BOFH in sight...
			for index, suit in enumerate(Suit.Suits):
				# Recurse for each suit!
				suit_split = filter(lambda card: card.suit == suit, cards)
				self.draw_cards(widget, suit_split, start, spacing, factor)
		else:
			for index, card in filter(lambda x: x[1], enumerate(cards)):
				pos_x = start[0] + spacing[0] * (index % factor)
				pos_y = start[1] + spacing[1] * (index / factor)
				self.draw_card(widget, card, pos_x, pos_y)

	def draw_table(self, widget):
		margin_x = margin_y = 16
		table_width, table_height = widget.get_size()
		card_width = self.card_mask.get_width() / 13
		card_height = self.card_mask.get_height() / 5
		spacing = (card_width/2, card_height/4)
			
		def build_args(position):
			args = {}
			if position in [Seat.North, Seat.South]: args['factor'] = 13
			else: args['factor'] = 12
			width = card_width + (args['factor'] - 1)*spacing[0]
			height = card_height + (13/args['factor'] - 1)*spacing[1]
			if position == Seat.North:
				args['start'] = ((table_width - width)/2, margin_y)
			elif position == Seat.South:
				args['start'] = ((table_width - width)/2, table_height-height-margin_y)
			elif position == Seat.East:
				args['start'] = (table_width-width-margin_x, (table_height - height)/2)
			elif position == Seat.West:
				args['start'] = (margin_x, (table_height - height)/2)
			return args

		for seat, hand in self.deck.hands.items():
			hand.sort()
			args = build_args(seat)
			self.draw_cards(widget, hand.cards, args['start'], spacing, args['factor'], False)

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
