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


from client.interface import IPybridgeClientListener


class GtkGladeListener:

	__implements__ = (IPybridgeClientListener,)

	def __init__(self, ui):
		self.ui = ui

	def gameCallMade(self, seat, call):
		print seat, call

	def gameCardPlayed(self, seat, card):
		print seat, card

	def gameContract(self, contract):
		pass

	def gameResult(self, result):
		pass

	def loginGood(self):
		self.ui.dialog_connection.window.hide()
		self.ui.window_main.window.show()

		hostname = "wibble"
		self.ui.window_main.message_add('connected', "Connected to %s" % hostname)

		# Get lists of active tables and online users.
		self.ui.connection.cmdListTables()
		self.ui.connection.cmdListUsers()

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

	def tableOpened(self, tablename):
		self.ui.window_main.table_add(tablename)

	def tableClosed(self, tablename):
		self.ui.window_main.table_remove(tablename)

	def tableListing(self, tables):
		self.ui.window_main.tables_update(tables)

	def userListing(self, users):
		self.ui.window_main.users_update(users)

	def userLoggedIn(self, username):
		self.ui.window_main.user_add(username)

	def userLoggedOut(self, username):
		self.ui.window_main.user_remove(username)
