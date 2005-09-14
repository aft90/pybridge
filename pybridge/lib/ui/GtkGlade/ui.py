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


from twisted.internet import gtk2reactor
gtk2reactor.install()
import gtk
from twisted.internet import reactor

import conf
from client.factory import PybridgeClientFactory
from client.interface import IPybridgeClientListener

from dialog_connection import DialogConnection
from window_bidbox import WindowBidbox
from window_calls import WindowCalls
from window_main import WindowMain


# Use getHandle() to instantiate the UI binding.

def getHandle():
	try:
		ui = GtkGladeUI()
	except GtkGladeUI, __instance:
		ui = __instance
	return ui


class GtkGladeUI:


	__instance = None


	def __init__(self):
		# Check for existing handler.
		if GtkGladeUI.__instance:
			raise GtkGladeUI.__instance
		GtkGladeUI.__instance = self
	
		self.config = conf  # configuration variables.


	def connect(self, address):
		reactor.connectTCP(address, 5040, PybridgeClientFactory())
		reactor.run()


	def disconnect(self):
		if reactor.running:
			# TODO: send quit
			reactor.stop()


	def run(self):
		self.dialog_connection = DialogConnection()
		gtk.main()  # Ready to roll.


	def shutdown(self):
		self.disconnect()
		gtk.main_quit()


	def window_close(self, window):
		pass


class GtkGladeListener:

	__implements__ = (IPybridgeClientListener,)
	

	def gameCallMade(self, seat, call):
		print seat, call


	def gameCardPlayed(self, seat, card):
		print seat, card


	def gameContract(self, contract):
		pass


	def gameResult(self, result):
		pass


	def observerJoins(self, observer):
		print 'observer joins', observer


	def observerLeaves(self, observer):
		print 'observer leaves', observer


	def playerJoins(self, player, seat):
		print 'player joins', player, seat


	def playerLeaves(self, player):
		print 'player leaves', player
