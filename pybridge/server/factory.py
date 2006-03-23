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


from twisted.internet.protocol import Factory
from twisted.python import components, log
import os.path, re, shelve, sys

from protocol import PybridgeServerProtocol
from table import BridgeTable


class PybridgeServerFactory(Factory):

	protocol = PybridgeServerProtocol


	def __init__(self):
		self.tables = {}  # For each table name, its Table object.
		self.users = {}   # For each online user name, its ServerProtocol instance.


	def startFactory(self):
		# Construct path to datafiles.
		dummyDir = "~/.pybridge/server"
		dbDir = os.path.expanduser(dummyDir)
		# Catch for OSes that do not have a $HOME.
		if dbDir == dummyDir:
			dbDir = "serverdata"
		dbDir = os.path.normpath(dbDir)
		if not os.path.isdir(dbDir):
			os.makedirs(dbDir)
		#logPath = os.path.join(dbDir, "log")
		#log.startLogging(open(logPath, 'w'), 0)
		log.startLogging(sys.stdout)  # Log to stdout.
		log.msg("Starting the PyBridge server.")
		# Load user account file.
		# TODO: replace user account file with a SQLite database.
		accountPath = os.path.join(dbDir, "db_accounts")
		self.accounts = shelve.open(accountPath, 'c', writeback=True)


	def stopFactory(self):
		log.msg("Stopping the PyBridge server.")
		self.informAllUsers(self, "shutdown")
		self.accounts.close()  # Save account information.


# Factory operations.


	def tableOpen(self, tablename):
		"""Creates a new table."""
		if tablename in self.tables:
			return "tablename already exists"
		table = BridgeTable(tablename)
		self.tables[tablename] = table
		self.informAllUsers("tableOpened", tablename)
		log.msg("Opened table %s" % tablename)


	def tableClose(self, tablename):
		"""Closes the specified table."""
		if tablename in self.tables:
#			self.tables[tablename].close()
			self.informAllUsers("tableClosed", tablename)
			del self.tables[tablename]
			log.msg("Closed table %s" % tablename)


	def tableAddUser(self, username, tablename):
		"""Adds user to table observer list."""
		table = self.tables.get(tablename)
		if table and username not in table.observers:
			table.observers[username] = self.users[username]
			self.informAllUsers("userJoinsTable", username, tablename)
			log.msg("User %s joins table %s" % (username, tablename))


	def tableRemoveUser(self, username, tablename):
		"""Removes user from table observer list."""
		table = self.tables.get(tablename)
		if table and username in table.observers:
			self.informAllUsers("userLeavesTable", username, tablename)
			del table.observers[username]
			log.msg("User %s leaves table %s" % (username, tablename))
			# If there are no remaining users, we should close table.
			if len(table.observers) == 0:
				self.tableClose(tablename)


	def userLogin(self, username, password, listener):
		"""Attempt login."""
		if username not in self.accounts:
			return "not registered"
		elif username in self.users:
			return "already logged in"
		elif self.accounts[username]['password'] == password:  # Password match.
			self.users[username] = listener
			self.informAllUsers("userLoggedIn", username)
			log.msg("User %s logged in" % username)
		else:
			return "incorrect password"


	def userLogout(self, username):
		if username in self.users:
			# Remove user from active tables.
			[self.tableRemoveUser(username, tablename) for tablename in self.tables]
			self.informAllUsers("userLoggedOut", username)
			del self.users[username]
			log.msg("User %s logged out" % username)


	def userRegister(self, username, password):
		"""Registers username+password in database."""
		if username in self.accounts:
			return "already registered"
		elif len(username) > 20:
			return "too many characters"
		elif re.search("[^A-Za-z0-9_]", username):
			return "invalid characters"
		else:
			self.accounts[username] = {'username' : username, 'password' : password}
			log.msg("New user %s registered" % username)


	def userTalk(self, sender, recipients, message):
		"""Sends message from sender to each recipient user."""
		# TODO: check silence lists.
		self.informUsers("messageReceived", recipients, sender, message)


# Utility functions.


	def informUsers(self, eventName, usernames, *args):
		"""For each given user, calls specified event with provided args."""
		for username in usernames:
			event = getattr(self.users[username], eventName)
			event(*args)


	def informAllUsers(self, eventName, *args):
		self.informUsers(eventName, self.users.keys(), *args)
