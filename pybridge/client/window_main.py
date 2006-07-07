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
from cardarea import CardArea
from wrapper import GladeWrapper

from connector import connector
from windowmanager import windowmanager
from pybridge.conf import PYBRIDGE_VERSION
from pybridge.environment import environment


class WindowMain(GladeWrapper):

	glade_name = 'window_main'


	def new(self):
		# Set up table listing.
		self.tablelisting_store = gtk.ListStore(str)
		self.tablelisting.set_model(self.tablelisting_store)
		cell_renderer = gtk.CellRendererText()
		for index, title in enumerate( ('Name',) ):
			column = gtk.TreeViewColumn(title, cell_renderer, text=index)
			self.tablelisting.append_column(column)
		# Get list of available tables.
		d = connector.listTables()
		d.addCallback(self.add_tables)


	def add_tables(self, tablenames):
		"""Adds a table to the table listing."""
		for tablename in tablenames:
			row = (tablename, )
			iter = self.tablelisting_store.append(row)


	def remove_tables(self, tablenames):
		"""Removes a table from the table listing."""
		
		def func(model, path, iter, user_data):
			if model.get_value(iter, 0) in user_data:
				model.remove(iter)
			return True
		
		self.tablelisting_store.foreach(func, tablenames)


	def join_table(self, tablename):
		"""Actions to perform when user joins a table."""
		for widget in (self.menuitem_newtable, self.toolbutton_newtable, self.toolbutton_jointable):
			widget.set_property('sensitive', False)
		
		# Set up card area widget as new page.
		tab = gtk.Label(tablename)
		self.cardarea = CardArea()
		self.cardarea.on_card_clicked = self.card_clicked
		self.cardarea.show()
		index = self.notebook.append_page(self.cardarea, tab)
		self.notebook.set_current_page(index)
		
		windowmanager.launch('window_game')


	def leave_table(self, tablename):
		"""Actions to perform when user leaves a table."""
		for widget in (self.menuitem_newtable, self.toolbutton_newtable, self.toolbutton_jointable):
			widget.set_property('sensitive', True)
		windowmanager.terminate('window_game')


# Signal handlers.


	def card_clicked(self, card):
		connector.table.playCard(card)


	def on_tablelisting_row_activated(self, widget, *args):
		if connector.table is None:
			iter = self.tablelisting_store.get_iter(args[0])
			tablename = self.tablelisting_store.get_value(iter, 0)
			d = connector.joinTable(tablename)
			d.addCallback(lambda r: self.join_table(tablename))


	def on_window_main_delete_event(self, widget, *args):
		windowmanager.shutdown()


	def on_newtable_activate(self, widget, *args):
		windowmanager.launch('dialog_newtable')


	def on_jointable_activate(self, widget, *args):
		print self.tablelisting.get_cursor()


	def on_disconnect_activate(self, widget, *args):
		connector.disconnect()
		windowmanager.terminate('window_main')
		windowmanager.launch('dialog_connection')


	def on_fullscreen_activate(self, widget, *args):
		if self.menu_fullscreen.active:
			self.window.fullscreen()
		else:
			self.window.unfullscreen()


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

