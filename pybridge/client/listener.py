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
		self.ui         = ui
		self.parameters = None
		self.tables     = {}
		self.users      = {}
		self.watching   = {}


	def gameCallMade(self, seat, call):
		print seat, call


	def gameCardPlayed(self, seat, card):
		print seat, card


	def gameContract(self, contract):
		pass


	def gameResult(self, result):
		pass


	def gameStarted(self):
		pass


	def loginFailure(self):
		self.ui.dialog_connection.connect_failure("Bad login.")


	def loginSuccess(self):
		self.parameters = self.ui.dialog_connection.get_connection_parameters()  # hackish?
		self.ui.dialog_connection.connect_success()
		self.ui.dialog_connection.window.hide()
		self.ui.window_main.window.show()
		self.ui.window_main.message_add('connected', "Connected to %s" % self.parameters['hostname'])
		# Get lists of active tables and online users.
		self.ui.connection.cmdListTables()
		self.ui.connection.cmdListUsers()


	def playerJoins(self, player, seat):
		print 'player joins', player, seat


	def playerLeaves(self, player):
		print 'player leaves', player


	def protocolSuccess(self, version):
		# Attempt to login to server.
		parameters = self.ui.dialog_connection.get_connection_parameters()
		if parameters['register']:
			self.ui.connection.cmdRegister(parameters['username'], parameters['password'])
		self.ui.connection.cmdLogin(parameters['username'], parameters['password'])


	def protocolFailure(self, version):
		self.ui.dialog_connection.connect_failure("Bad protocol.")


	def tableOpened(self, tablename):
		self.tables[tablename] = {}
		self.ui.window_main.update_tables(self.tables)


	def tableClosed(self, tablename):
		del self.tables[tablename]
		self.ui.window_main.update_tables(self.tables)


	def tableListing(self, tables):
		self.tables.clear()
		for tablename in tables:
			self.tables[tablename] = {}
		self.ui.window_main.update_tables(self.tables)


	def userJoinsTable(self, username, tablename):
		if username == self.parameters['username']:
			# The user is the observer, so create a card table.
			#self.ui.window_main.table_listing.set_sensitivity(False)
			self.ui.window_main.create_cardtable(tablename)


	def userLeavesTable(self, username, tablename):
		if username == self.parameters['username']:
			print "left the table"
		print 'observer leaves', observer


	def userListing(self, users):
		self.users.clear()
		for username in users:
			self.users[username] = {}
		self.ui.window_main.update_users(self.users)


	def userLoggedIn(self, username):
		self.users[username] = {}
		self.ui.window_main.update_users(self.users)


	def userLoggedOut(self, username):
		del self.users[username]
		self.ui.window_main.update_users(self.users)
