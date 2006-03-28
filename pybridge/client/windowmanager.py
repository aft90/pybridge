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
from twisted.internet import reactor

from pybridge.environment import CLIENT_SETTINGS_PATH
from settings import settings


class WindowManager:


	def __init__(self):
		self._instances = {}


	def get(self, windowname):
		return self._instances.get(windowname, None)


	def launch(self, windowname):
		"""Launches specified window."""
		if windowname not in self._instances:
			
			if windowname == 'dialog_connection':
				from dialog_connection import DialogConnection
				instance = DialogConnection()
			elif windowname == 'dialog_newtable':
				from dialog_newtable import DialogNewtable
				instance = DialogNewtable()
			elif windowname == 'window_bidbox':
				from window_bidbox import WindowBidbox
				instance = WindowBidbox()
			elif windowname == 'window_calls':
				from window_calls import WindowCalls
				instance = WindowCalls()
			elif windowname == 'window_main':
				from window_main import WindowMain
				instance = WindowMain()
			elif windowname == 'window_tablelisting':
				from window_tablelisting import WindowTablelisting
				instance = WindowTablelisting()
			
			self._instances[windowname] = instance


	def terminate(self, windowname):
		self._instances[windowname].window.destroy()
		del self._instances[windowname]


	def shutdown(self):
		"""Bring everything to a stop, in a clean fashion."""
		
		# Save settings.
		settings.write(file(CLIENT_SETTINGS_PATH, 'w'))
		
		# Close down the shop.
		reactor.stop()
		gtk.main_quit()


windowmanager = WindowManager()

