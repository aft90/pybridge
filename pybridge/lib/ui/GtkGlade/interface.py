#!/usr/bin/env python

import os, sys
import gtk, gtk.glade

glade_file = "pybridge.glade"
glade_dir = ""

class Window(dict):
	def __init__(self):
		glade_path = os.path.join(glade_dir, glade_file)
		self.glade = gtk.glade.XML(glade_path, self.window_name, None)
		self.window = self.glade.get_widget(self.window_name)
		self.signal_autoconnect()
		self.new()
	
	def __getattr__(self, name):
		""" Allows referencing of Glade widgets as class attributes. """
		if name in self: return self[name]
		else:
			widget = self.glade.get_widget(name)
			if widget != None:
				self[name] = widget
				return widget
			else: raise AttributeError, name
	
	def __setattr__(self, name, value):
		self[name] = value
	
	def signal_autoconnect(self):
		""" Sets up class methods as named signal handlers. """
		signals = {}
		for attribute_name in dir(self):
			attribute = getattr(self, attribute_name)
			if callable(attribute):
				signals[attribute_name] = attribute
		self.glade.signal_autoconnect(signals)

	def new(self): pass

	def run(self): gtk.main()

## START CUSTOM DEFINITIONS ##

class WindowMain(Window):
	window_name = 'window_main'

	def new(self):
		# Set up card table.
		self.card_table.set_size_request(width = 600, height = 300)
		self.card_table.connect("configure_event", self.configure_event)
		self.card_table.connect("expose_event", self.expose_event)
		# Set up card table background.
		self.background_color = gtk.gdk.color_parse("#393")
		self.background = 0
		# Load card faces into a pixbuf. We expect 13 x 5 unit cards.
		self.cards = gtk.gdk.pixbuf_new_from_file("pixmaps/bonded.png")
		self.window_auction = WindowAuction()
		self.window_bidbox = WindowBidbox()

	def configure_event(self, widget, event):
		""" . """
		x, y, width, height = widget.get_allocation()
		self.backing = gtk.gdk.Pixmap(widget.window, width, height)
		self.backing.draw_rectangle(widget.get_style().white_gc, True, 0, 0, width, height)
		self.draw_card(self.backing, 50, 50, rank = 14, suit = 'club')
		return True

	def expose_event(self, widget, event):
		""" """
		x, y, width, height = event.area
		widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL], self.backing, x, y, x, y, width, height)
		return False

	def draw_card(self, widget, destX, destY, rank = None, suit = None, rotate = False):
		ranks = [14, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
		suits = ['club', 'diamond', 'heart', 'spade']
		# Get width and height of card from pixbuf.
		width = self.cards.get_width() / 13
		height = self.cards.get_height() / 5
		# Can we render a known card?
		if rank in ranks and suit in suits:
			# Calculate co-ordinates for front of card.
			srcX = ranks.index(rank) * width
			srcY = suits.index(suit) * height
		else:
			# Specify co-ordinates for back of card.
			srcX = width * 2
			srcY = height * 4
		# Now draw card to widget.
		widget.draw_pixbuf(None, self.cards, srcX, srcY, destX, destY, width, height)

	def draw_hands(self, widget, hands):
		pass

class WindowAuction(Window):
	window_name = 'window_auction'

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


class WindowBidbox(Window):
	window_name = 'window_bidbox'

class DialogAbout(Window):
	window_name = 'dialog_about'

	def new(self):
		self.dialog_about.set_name('PyBridge Client')
		self.dialog_about.set_version('0.0.1')
		self.dialog_about.set_copyright('Copyright 2004-2005 Michael Banks, Sourav K Mandal')
		self.dialog_about.set_website('http://pybridge.sourceforge.net/')
		self.dialog_about.set_website_label('PyBridge Home')
		self.dialog_about.set_authors(['Michael Banks <michaelbanks@dsl.pipex.com>', 'Sourav K Mandal <sourav@sourav.net>'])
		self.dialog_about.set_artists(['Stephen Banks <djbanksie@dsl.pipex.com>'])

## END CUSTOM DEFINITIONS ##

if __name__ == '__main__':
	interface = WindowMain()
	interface.run()
