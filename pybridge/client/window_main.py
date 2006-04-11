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
		self.cardarea = CardArea()
		self.cardarea.on_card_clicked = self.card_clicked
		self.scrolled_cardarea.add_with_viewport(self.cardarea)
		self.cardarea.show()
		
		windowmanager.launch('window_tablelisting')


	def join_table(self, tablename):
		"""Actions to perform when user joins a table."""
		self.button_newtable.set_property('sensitive', False)
		self.menuitem_newtable.set_property('sensitive', False)
		windowmanager.launch('window_game')


	def leave_table(self, tablename):
		"""Actions to perform when user leaves a table."""
		self.button_newtable.set_property('sensitive', True)
		self.menuitem_newtable.set_property('sensitive', True)
		windowmanager.destroy('window_game')


# Signal handlers.


	def card_clicked(self, card):
		print card


	def on_window_main_delete_event(self, widget, *args):
		windowmanager.shutdown()


	def on_newtable_activate(self, widget, *args):
		windowmanager.launch('dialog_newtable')


	def on_tablelisting_toggled(self, widget, *args):
		window = windowmanager.get('window_tablelisting').window
		if self.button_tablelisting.get_active():
			window.show()
		else:
			window.hide()


	def on_disconnect_activate(self, widget, *args):
		#connector.disconnect()
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

