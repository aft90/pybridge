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
from twisted.internet.protocol import ClientCreator

import conf
from client.protocol import PybridgeClientProtocol
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

		# Get configuration variables.
		self.config = conf

		self.connection = None  # Connection reference.


	def connect(self, parameters):
		"""Attempt to connect to Pybridge server with parameters."""

		def connected(connection):
			# Set up connection reference and listener.
			self.connection = connection
			self.connection.setListener(GtkGladeListener())
		
		if self.connection is None:
			creator = ClientCreator(reactor, PybridgeClientProtocol)
			defer = creator.connectTCP(parameters['host'], parameters['port'])
			defer.addCallback(connected)


	def load_main(self):
		self.window_main = WindowMain()
		self.window_bidbox = WindowBidbox()
		self.window_calls = WindowCalls()


	def run(self):
		"""Starts the graphical interface."""
		self.dialog_connection = DialogConnection()
		reactor.run()  # Start Twisted layer.
		gtk.main()     # Start GTK main loop.


	def shutdown(self):
		"""Bring everything to a stop."""
		reactor.stop()
		gtk.main_quit()


class GtkGladeListener:

	__implements__ = (IPybridgeClientListener,)

	def __init__(self):
		self.ui = getHandle()

	def gameCallMade(self, seat, call):
		print seat, call

	def gameCardPlayed(self, seat, card):
		print seat, card

	def gameContract(self, contract):
		pass

	def gameResult(self, result):
		pass

	def loginGood(self):
		self.ui.dialog_connection.widget.hide()
		self.ui.load_main()

	def loginBad(self):
		print "eek"

	def observerJoins(self, observer):
		print 'observer joins', observer

	def observerLeaves(self, observer):
		print 'observer leaves', observer

	def playerJoins(self, player, seat):
		print 'player joins', player, seat

	def playerLeaves(self, player):
		print 'player leaves', player

	def protocolGood(self, version):
		# Attempt to login to server.
		parameters = self.ui.dialog_connection.get_connection_parameters()
		self.ui.connection.cmdLogin(parameters['username'], parameters['password'])

	def protocolBad(self, version):
		self.ui.dialog_connection.failure()
