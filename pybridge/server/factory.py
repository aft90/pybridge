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
from pybridge.strings import Error, Event


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
		self.informAllUsers(self, Event.SERVER_SHUTDOWN)
		self.accounts.close()  # Save account information.


# Factory operations.


	def tableOpen(self, tablename):
		"""Creates a new table."""
		if tablename in self.tables:
			return Error.TABLE_EXISTS
		elif not self.testSanity(tablename):
			return Error.TABLE_BADNAME
		table = BridgeTable(tablename)
		self.tables[tablename] = table
		self.informAllUsers(Event.TABLE_OPENED, tablename)
		log.msg("Opened table %s" % tablename)


	def tableClose(self, tablename):
		"""Closes the specified table."""
		if tablename in self.tables:
#			self.tables[tablename].close()
			self.informAllUsers(Event.TABLE_CLOSED, tablename)
			del self.tables[tablename]
			log.msg("Closed table %s" % tablename)


	def tableAddUser(self, username, tablename):
		"""Adds user to table observer list."""
		table = self.tables.get(tablename)
		if table and username not in table.observers:
			table.observers[username] = self.users[username]
			self.informAllUsers(Event.TABLE_USERJOINS, username, tablename)
			log.msg("User %s joins table %s" % (username, tablename))


	def tableRemoveUser(self, username, tablename):
		"""Removes user from table observer list."""
		table = self.tables.get(tablename)
		if table and username in table.observers:
			self.informAllUsers(Event.TABLE_USERLEAVES, username, tablename)
			del table.observers[username]
			log.msg("User %s leaves table %s" % (username, tablename))
			# If there are no remaining users, we should close table.
			if len(table.observers) == 0:
				self.tableClose(tablename)


	def userLogin(self, username, password, listener):
		"""Attempt login."""
		if username not in self.accounts:
			return Error.LOGIN_NOACCOUNT
		elif username in self.users:
			return Error.LOGIN_ALREADY
		elif self.accounts[username]['password'] == password:  # Password match.
			self.users[username] = listener
			self.informAllUsers(Event.USER_LOGGEDIN, username)
			log.msg("User %s logged in" % username)
		else:
			return Error.LOGIN_BADPASSWORD


	def userLogout(self, username):
		if username in self.users:
			# Remove user from table.
			if self.users[username].table != None:
				tablename = self.users[username].table.name
				self.tableRemoveUser(username, tablename)
			self.informAllUsers(Event.USER_LOGGEDOUT, username)
			del self.users[username]
			log.msg("User %s logged out" % username)


	def userRegister(self, username, password):
		"""Registers username+password in database."""
		if username in self.accounts:
			return Error.USER_REGISTERED
		elif not self.testSanity(username):
			return Error.USER_BADNAME
		else:
			self.accounts[username] = {'username' : username, 'password' : password}
			log.msg("New user %s registered" % username)


	def userTalk(self, sender, recipients, message):
		"""Sends message from sender to each recipient user."""
		# TODO: check silence lists.
		self.informUsers(Event.TALK_MESSAGE, recipients, sender, message)


# Utility functions.


	def informUsers(self, eventName, usernames, *args):
		"""For each given user, calls specified event with provided args."""
		for username in usernames:
			event = getattr(self.users[username], eventName)
			event(*args)


	def informAllUsers(self, eventName, *args):
		"""Same as informUsers, but informs all users."""
		self.informUsers(eventName, self.users.keys(), *args)


	def testSanity(self, word):
		"""Checks a given word for invalid characters."""
		return 0 < len(word) <= 20 and not re.search("[^A-Za-z0-9_]", word)
