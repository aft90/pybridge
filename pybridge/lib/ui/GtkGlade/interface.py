import os, sys
import gtk, gtk.glade

glade_file = "pybridge.glade"
glade_dir = "/home/michael/projects/pybridge/pybridge/lib/ui/GtkGlade/"

pixmaps_dir = "/home/michael/projects/pybridge/pybridge/lib/ui/GtkGlade/pixmaps/"

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

class WindowMain(Window):
	window_name = 'window_main'

	def new(self):
		# Initialise child windows and dialogs.
		self.window_bidbox = WindowBidbox()
		self.window_bidding = WindowBidding()
		self.window_rooms = WindowRooms()
		self.dialog_about = DialogAbout()
		self.dialog_serverconnect = DialogServerconnect()
		# Set up card table.
		self.card_table.set_size_request(width = 600, height = 400)
		self.card_table.connect("configure_event", self.configure_event)
		self.card_table.connect("expose_event", self.expose_event)
		# Set up card table background.
		background_color = gtk.gdk.color_parse("#015A01")
		self.card_table.modify_bg(gtk.STATE_NORMAL, background_color)
		# Load card mask into a pixbuf. We expect 13 x 5 unit cards.
		card_mask_path = os.path.join(pixmaps_dir, "bonded.png")
		self.card_mask = gtk.gdk.pixbuf_new_from_file(card_mask_path)
	
	def set_state(self, state):
		if state == 'bidding':
			self.window_bidbox.window.show()
			self.window_bidding.window.show()
		elif state == 'play':
			pass
	
	def server_connect(self):
		""" """
		pass

	def server_disconnect(self):
		""" """
		# if currently in game, ask.
		pass

	def configure_event(self, widget, event):
		""" Creates backing pixmap of the appropriate size. """
		x, y, width, height = widget.get_allocation()
		self.backing = gtk.gdk.Pixmap(widget.window, width, height)
		self.backing.draw_rectangle(widget.get_style().bg_gc[gtk.STATE_NORMAL],
		                            True, 0, 0, width, height)
		self.draw_hand(self.backing, range(1,14), 100, 20, 24, False)
		self.draw_hand(self.backing, range(1,14), 100, 300, 24, False)
		self.draw_hand(self.backing, range(1,14), 20, 20, 24, True)
		self.draw_hand(self.backing, range(1,14), 500, 20, 24, True)
		return True

	def expose_event(self, widget, event):
		""" Redraws the screen from the backing pixmap. """
		x, y, width, height = event.area
		widget.window.draw_drawable(widget.get_style().bg_gc[gtk.STATE_NORMAL],
		                            self.backing, x, y, x, y, width, height)
		return False
	
	def draw_card(self, widget, card, destX, destY, rotate = False):
		ranks = [14, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
		suits = ['club', 'diamond', 'heart', 'spade']
		# Get width and height of card from pixbuf.
		width = self.card_mask.get_width() / 13
		height = self.card_mask.get_height() / 5
		# Can we render a known card?
		#if card.rank in ranks and card.suit in suits:
		#	# Calculate co-ordinates for front of card.
		#	srcX = ranks.index(card.rank) * width
		##	srcY = suits.index(card.suit) * height
		#else:
			# Specify co-ordinates for back of card.
		srcX = width * 2
		srcY = height * 4
		# Now draw card to widget.
		widget.draw_pixbuf(None, self.card_mask, srcX, srcY, destX, destY, width, height)

	def draw_hand(self, widget, hand, destX, destY, offset, rotate = False):
		for card in hand:
			self.draw_card(widget, card, destX, destY, rotate)
			if rotate: destY += offset
			else: destX += offset

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
	
class WindowBidding(Window):
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

class WindowBidbox(Window):
	window_name = 'window_bidbox'

class WindowRooms(Window):
	window_name = 'window_rooms'

	def new(self):
		self.room_tree_model = gtk.TreeStore(str, str, str)
		self.room_tree.set_model(self.room_tree_model)
		self.model_iter = self.room_tree_model.insert_after(parent = None, sibling = None)

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

class DialogServerconnect(Window):
	window_name = 'dialog_serverconnect'

	def new(self):
		pass
