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
from table import Table


class PybridgeServerFactory(Factory):

	protocol = PybridgeServerProtocol


	def __init__(self):
		self.listeners = {}  # Listener objects, keyed by username.
		self.tables    = {}  # Table objects, keyed by tablename.


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

		# Advise each listener that server is shutting down.
		[user.shutdown() for user in self.listeners.values()]

		# Save account information.
		self.accounts.close()


	def getTable(self, tablename):
		"""Returns table object associated with tablename."""
		if tablename in self.tables:
			return self.tables[tablename]


	def getTableList(self):
		return self.tables.keys()


	def getUserList(self):
		"""Returns a list of all registered users."""
		return self.listeners.keys()


	def accountFieldRetrieve(self, accountname, field):
		"""Returns the value of field for given account."""
		if field in ("username", ):
			if accountname in self.accounts:
				return self.accounts[accountname][field]
		return False


	def tableOpen(self, tablename):
		"""Creates a new table object with given identifier."""
		if not tablename in self.tables:
			# Table with tablename must not exist already.
			self.tables[tablename] = Table(tablename)
			[listener.tableOpened(tablename) for listener in self.listeners.values()]
			self.log.msg("Opened table %s" % tablename)


	def tableClose(self, tablename):
		"""Closes the table object with given identifier."""
		if tablename in self.tables:
			table = self.tables[tablename]
			table.close()
			[listener.tableClosed(tablename) for listener in self.listeners.values()]
			del self.tables[tablename]
			self.log.msg("Closed table %s" % tablename)


	def userAuth(self, username, password):
		"""Returns True if username+password may login, False otherwise."""
		if username not in self.accounts:
			# User account does not exist.
			return False
		elif username in self.listeners:
			# User with username is already logged in.
			return False
		else:
			# Check for password match.
			return self.accounts[username]['password'] == password


	def userLogin(self, username, password, listener):
		"""Attempt to login."""
		if self.userAuth(username, password):
			self.listeners[username] = listener
			[listener.userLoggedIn(username) for listener in self.listeners.values()]
			self.log.msg("Login succeeded for user %s" % username)
		else:
			self.log.msg("Login attempt failed (username %s)" % username)


	def userLogout(self, username):
		if username in self.listeners:
			[listener.userLoggedOut(username) for listener in self.listeners.values()]
			del self.listeners[username]
			self.log.msg("Logout succeeded for user %s" % username)


	def userRegister(self, username, password):
		"""Registers username+password in database."""
		if username in self.accounts:
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
