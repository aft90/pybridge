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
from wrapper import WidgetWrapper

import lib_cardtable  # Card table library functions.


class WindowMain(WidgetWrapper):

	widget_name = 'window_main'


	def new(self):
		# Set up card table.
		self.card_table.set_size_request(width=720, height=540)
		self.card_table.connect("configure_event", lib_cardtable.configure_event)
		self.card_table.connect("expose_event", lib_cardtable.expose_event)
		self.card_table.connect("button_press_event", lib_cardtable.button_press_event)
		self.card_table.add_events(gtk.gdk.BUTTON_PRESS_MASK)		


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


	def on_statusbar_activate(self, widgets, *args):
		if self.statusbar_main.get_property('visible'):
			self.statusbar_main.hide()
		else:
			self.statusbar_main.show()


	def on_pybridge_home_activate(self, widget, *args):
		webbrowser.open('http://pybridge.sourceforge.net/')


	def on_about_activate(self, widget, *args):
		print self.interface.config
		dialog_about = gtk.AboutDialog()
		dialog_about.set_name("PyBridge Client")
		dialog_about.set_version('0.1')
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
