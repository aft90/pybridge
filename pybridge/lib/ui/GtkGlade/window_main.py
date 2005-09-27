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


	def update_tables(self, tables):
		"""Update listing of tables."""
		self.table_store.clear()
		for table in tables.keys():  # for now
			iter = self.table_store.append()
			self.table_store.set_value(iter, 0, table)


	def update_users(self, users):
		"""Update listing of users."""
		self.user_store.clear()
		for user in users.keys():
			iter = self.user_store.append()
			self.user_store.set_value(iter, 0, user)


	# Signal handlers


	def on_window_main_destroy(self, widget, *args):
		self.ui.shutdown()


	def on_newtable_activate(self, widget, *args):
		self.ui.dialog_newtable.window.show()


	def on_disconnect_activate(self, widget, *args):
		self.ui.connection.cmdQuit()


	def on_quit_activate(self, widget, *args):
		self.on_window_main_destroy(widget, *args)


	def on_table_listing_row_activated(self, widget, *args):
		# Get name of selected table.
		iter = self.table_store.get_iter(args[0])  # path value
		tablename = self.table_store.get_value(iter, 0)
		self.ui.connection.cmdTableObserve(tablename)


	def on_statusbar_activate(self, widget, *args):
		if self.statusbar_main.get_property('visible'):
			self.statusbar_main.hide()
		else:
			self.statusbar_main.show()


	def on_pybridge_home_activate(self, widget, *args):
		webbrowser.open('http://pybridge.sourceforge.net/')


	def on_about_activate(self, widget, *args):
		self.ui.dialog_about.window.show()
