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

import gtk, gtk.glade
import ui

from pybridge.environment import environment

ICON_PATH = environment.find_pixmap("pybridge.png")
GLADE_PATH = environment.find_glade("pybridge.glade")

class WindowWrapper(dict):

	def __init__(self):
		self.glade = gtk.glade.XML(GLADE_PATH, self.window_name, None)
		self.window = self.glade.get_widget(self.window_name)
		self.window.set_icon_from_file(ICON_PATH)
		self.signal_autoconnect()
		self.ui = ui.getHandle()
		self.new()

	def __getattr__(self, name):
		"""Allows referencing of Glade widgets as window attributes."""
		if name in self:
			return self[name]
		else:
			widget = self.glade.get_widget(name)
			if widget != None:
				self[name] = widget  # Saves time later.
				return widget
			else:
				raise AttributeError(name)

	def __setattr__(self, name, value):
		self[name] = value

	def signal_autoconnect(self):
		"""Sets up class methods as named signal handlers."""
		signals = {}
		for attribute_name in dir(self):
			attribute = getattr(self, attribute_name)
			if callable(attribute):
				signals[attribute_name] = attribute
		self.glade.signal_autoconnect(signals)

	def new(self):
		pass
