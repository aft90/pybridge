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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from twisted.internet.protocol import Factory
from twisted.python import components, log
import os.path, re, shelve, sys

from protocol import PybridgeServerProtocol
from table import BridgeTable, TableError


class PybridgeServerFactory(Factory):

	protocol = PybridgeServerProtocol


	def __init__(self):
		self.listeners = {}  # For each username, the respective FactoryListener object.
		self.tables    = {}  # For each tablename, the respective Table object.


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

		# Set up logging.
		logPath = os.path.join(dbDir, "log")
		self.log = log
		#self.log.startLogging(open(logPath, 'w'), 0)
		self.log.startLogging(sys.stdout)
		self.log.msg("Starting the PyBridge server.")

		# Load user account file.
		accountPath = os.path.join(dbDir, "db_accounts")
		self.accounts = shelve.open(accountPath, 'c', writeback=True)


	def stopFactory(self):
		self.log.msg("Stopping the PyBridge server.")
		[listener.shutdown() for listener in self.listeners.values()]
		self.accounts.close()  # Save account information.


	def getTable(self, tablename):
		"""Returns table object associated with tablename."""
		return self.tables.get(tablename, None)


	def getTablesList(self):
		"""Returns a list of all active tablenames."""
		return self.tables.keys()


	def getUsersList(self):
		"""Returns a list of all online usernames."""
		return self.listeners.keys()


	def getUsersAtTableList(self, tablename):
		"""Returns a list of all usernames watching given table."""
		return self.tables[tablename].listeners.keys()


	def getTablesForUserList(self, username):
		"""Returns a list of all tablenames that username is watching."""
		tables = []
		for tablename, table in self.tables.items():
			if username in table.listeners:
				tables.append(tablename)
		return tables


	def accountFieldRetrieve(self, accountname, field):
		"""Returns the value of field for given account."""
		if field in ("username", ):  # TODO: add more fields!
			if accountname in self.accounts:
				return self.accounts[accountname][field]
		return False


	def tableOpen(self, tablename):
		"""Creates a new table object with given identifier."""
		if not tablename in self.tables:
			# Table with tablename must not exist already.
			self.tables[tablename] = BridgeTable(tablename)
			[listener.tableOpened(tablename) for listener in self.listeners.values()]
			self.log.msg("Opened table %s" % tablename)
			return True
		return False


	def tableClose(self, tablename):
		"""Closes the table object with given identifier."""
		if tablename in self.tables:
			table = self.tables[tablename]
			table.close()
			[listener.tableClosed(tablename) for listener in self.listeners.values()]
			del self.tables[tablename]
			self.log.msg("Closed table %s" % tablename)


	def tableAddListener(self, username, tablename, tablelistener):
		"""Adds table listener object associated with username, to table observer list."""
		if self.tables[tablename]:
			self.tables[tablename].listeners[username] = tablelistener
			[listener.userJoinsTable(username, tablename) for listener in self.listeners.values()]
			self.log.msg("User %s joins table %s" % (username, tablename))
			return True
		return False


	def tableRemoveListener(self, username, tablename):
		"""Removes table listener object associated with username, from table observer list."""
		if self.tables[tablename]:
			del self.tables[tablename].listeners[username]
			[listener.userLeavesTable(username, tablename) for listener in self.listeners.values()]
			self.log.msg("User %s leaves table %s" % (username, tablename))
			# TODO: Check if we should close table.
			return True
		return False


	def userLogin(self, username, password, factorylistener):
		"""Attempt to login. Returns True if successful, False otherwise."""
		# Check for spurious login requests.
		if username not in self.accounts:
			self.log.msg("Login attempt failed for username %s: not registered" % username)
			return False
		if username in self.listeners:
			self.log.msg("Login attempt failed for username %s: already logged in" % username)
			return False
		# Check for password match.
		if self.accounts[username]['password'] == password:
			self.listeners[username] = factorylistener
			[listener.userLoggedIn(username) for listener in self.listeners.values()]
			self.log.msg("Login succeeded for user %s" % username)
			return True
		else:
			self.log.msg("Login attempt failed for username %s: bad password" % username)
			return False


	def userLogout(self, username):
		if username in self.listeners:
			# Remove user from active tables.
			tables = self.getTablesForUserList(username)
			[self.tableRemoveListener(username, tablename) for tablename in tables]
			# Inform all clients that user has logged out.
			[listener.userLoggedOut(username) for listener in self.listeners.values()]
			del self.listeners[username]
			self.log.msg("Logout succeeded for user %s" % username)


	def userRegister(self, username, password):
		"""Registers username+password in database."""
		if username in self.accounts:
			self.log.msg("Registration failed for username %s: already registered" % username)
			return False
		
		# Check username for well-formedness.
		if len(username) > 20:
			return False

		# TODO: check that username A-Za-z0-9\_ (\w?)

		self.accounts[username] = {
			'username' : username,
			'password' : password,
		}
		self.log.msg("Registration succeeded for user %s" % username)
		return True


	def userTalk(self, speaker, receipients, message):
		"""Sends message from speaker to each user in receipients."""
		# TODO: check silence lists.
		# TODO: profanity filter on message. (maybe client side?)
		for username in recepients:
			user = self.listeners.get(username, None)
			if user:
				user.messageReceived(speaker, message)
		return True
