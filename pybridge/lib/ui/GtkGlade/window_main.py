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


import gtk, webbrowser

import lib_cardtable  # Card table library functions.
from wrapper import WindowWrapper
from lib.core.enumeration import Seat


class WindowMain(WindowWrapper):

	window_name = 'window_main'


	def new(self):
		cell_renderer = gtk.CellRendererText()
		
		# Set up table listing.
		self.table_store = gtk.ListStore(str, str, str)
		self.table_listing.set_model(self.table_store)
		for index, title in enumerate(('Title', 'Players', 'Observers')):
			column = gtk.TreeViewColumn(title, cell_renderer, text=index)
			self.table_listing.append_column(column)

		# Set up user listing.
		self.user_store = gtk.ListStore(str)
		self.user_listing.set_model(self.user_store)
		for index, title in enumerate(('Name',)):
			column = gtk.TreeViewColumn(title, cell_renderer, text=index)
			self.user_listing.append_column(column)

#		self.create_cardtable("the good guy")
	

	def create_cardtable(self, title):
		"""Builds a new card table and tab widget with title."""
		tab = gtk.Label(title)
		card_table = gtk.DrawingArea()
		card_table.connect("configure_event", lib_cardtable.configure_event)
		card_table.connect("expose_event", lib_cardtable.expose_event)
		card_table.connect("button_press_event", lib_cardtable.button_press_event)
		card_table.add_events(gtk.gdk.BUTTON_PRESS_MASK)		
		card_table.show()
		self.notebook.append_page(card_table, tab)


	def message_add(self, symbol, message):
		"""Adds message with identifying symbol to statusbar."""
		context = self.statusbar.get_context_id(symbol)
		self.statusbar.push(context, message)


	def message_remove(self, symbol):
		"""Removes message with identifying symbol from statusbar."""
		context = self.statusbar.get_context_id(symbol)
		self.statusbar.pop(context)


	def table_add(self, tablename):
		iter = self.table_store.append()
		self.table_store.set_value(iter, 0, tablename)


	def table_remove(self, table):
		print "table remove not implemented"


	def tables_update(self, tables):
		"""Update listing of tables."""
		self.table_store.clear()
		for table in tables:
			iter = self.table_store.append()
			self.table_store.set_value(iter, 0, table['title'])
			players = str.join(", ", (table[Seat.North], table[Seat.East], table[Seat.South], table[Seat.West]))
			self.table_store.set_value(iter, 1, players)


	def user_add(self, username):
		iter = self.user_store.append()
		user_store.set_value(iter, 0, username)


	def user_remove(self, username):
		pass


	def users_update(self, users):
		pass


	def table_remove(self, table):
		print "table remove not implemented"


	def tables_update(self, tables):
		"""Update listing of tables."""
		self.table_store.clear()
		for table in tables:
			iter = self.table_store.append()
			self.table_store.set_value(iter, 0, table['title'])
			players = str.join(", ", (table[Seat.North], table[Seat.East], table[Seat.South], table[Seat.West]))
			self.table_store.set_value(iter, 1, players)


	def user_add(self, username):
		iter = self.table_store.append()


	# Signal handlers


	def on_window_main_destroy(self, widget, *args):
		self.ui.shutdown()

	def on_newtable_activate(self, widget, *args):
		self.ui.dialog_newtable.window.show()

	def on_quit_activate(self, widget, *args):
		print "Check exit confirmation from user."
		self.on_window_main_destroy(widget, *args)


	def on_table_listing_row_activated(self, widget, *args):
		print "ok", widget, args

	def on_statusbar_activate(self, widget, *args):
		if self.statusbar_main.get_property('visible'):
			self.statusbar_main.hide()
		else:
			self.statusbar_main.show()

	def on_pybridge_home_activate(self, widget, *args):
		webbrowser.open('http://pybridge.sourceforge.net/')

	def on_about_activate(self, widget, *args):
		self.ui.dialog_about.window.show()
