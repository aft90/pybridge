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


import gtk
from wrapper import GladeWrapper

from connector import connector
from windowmanager import windowmanager


class WindowTablelisting(GladeWrapper):

	glade_name = 'window_tablelisting'


	def new(self):
		parent = windowmanager.get('window_main')
		self.window.set_transient_for(parent)

		cell_renderer = gtk.CellRendererText()
		self.table_store = gtk.ListStore(str, str)
		self.table_listing.set_model(self.table_store)
		for index, title in enumerate(('Name', 'Status')):
			column = gtk.TreeViewColumn(title, cell_renderer, text=index)
			self.table_listing.append_column(column)
		
		# Get list of open tables.
		connector.listTables().addCallback(self.add_tables)


	def add_tables(self, tablenames):
		"""Adds a table to the table listing."""
		for tablename in tablenames:
			row = (tablename, '')
			iter = self.table_store.append(row)


	def remove_table(self, tablenames):
		"""Removes a table from the table listing."""
		
		def func(model, path, iter, user_data):
			if model.get_value(iter, 0) in user_data:
				model.remove(iter)
			return True
		
		self.table_store.foreach(func, tablenames)


# Signal handlers.


	def on_table_listing_delete_event(self, widget, *args):
		windowmanager.get('window_main').button_tablelisting.set_active(False)
		self.window.hide()
		return True  # Stops deletion taking place.


	def on_table_listing_row_activated(self, widget, *args):
		
		def success(reference):
			windowmanager.get('window_main').join_table(tablename)
		
		iter = self.table_store.get_iter(args[0])
		tablename = self.table_store.get_value(iter, 0)
		connector.joinTable(tablename).addCallback(success)

