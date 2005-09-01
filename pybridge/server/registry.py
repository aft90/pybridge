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


import shelve, os.path

from table import Table


# Note: don't instantiate Registry directly. Use getHandle().

def getHandle():
	try:
		registry = Registry()
	except Registry, instance:
		registry = instance
	return registry


class Registry:

	__instance = None

	_users    = {}  # Existing user objects, keyed by user identifier.
	_tables   = {}  # Existing table objects, keyed by table identifier.

	
	def __init__(self):
		# Check for existing handler.
		if Registry.__instance:
			raise Registry.__instance
		Registry.__instance = self

		# Construct path to datafile.
		dummyDir = "~/.pybridge/server"
		dbDir = os.path.expanduser(dummyDir)
		# Catch for OSes that do not have a $HOME.
		if dbDir == dummyDir:
			dbDir = "serverdata"
		dbDir = os.path.normpath(dbDir)
		if not os.path.isdir(dbDir):
			os.makedirs(dbDir)
		# TODO: check for lock file.
		pathAccounts = os.path.join(dbDir, "db_accounts")
		self._accounts = shelve.open(pathAccounts, "c", writeback=True)
		

	def close(self):
		"""Save account information to datafile."""
		# Since we modify self._users, we must copy keys as tuple.
		for identifier in self._users.keys():
			self.userLogout(identifier)
		self._accounts.close()  # Save user registry.


	def getFinger(self, identifier):
		"""Returns a dict of public information about user."""
		if identifier in self._accounts:
			return self._accounts['identifier']  # TODO: limit fields.
		else:  # No such user.
			return False


	def getUser(self, identifier):
		"""Returns user object associated with identifier."""
		if identifier in self._users:
			return self._users[identifier]


	def getTable(self, identifier):
		"""Returns table object associated with identifier."""
		if identifier in self._tables:
			return self._tables[identifier]
			


	def getVariable(self, identifier, name):
		""""""
		# TODO: improve
		if self._accounts[identifier]:
			if self._accounts[identifier][name]:
				return self._accounts[identifier][name]
		return False


	def setVariable(self, identifier, name, value):
		""""""
		if self.getVariable(identifier, name):
			self._accounts[identifier][name] = value


	def tableCreate(self, identifier):
		table = Table(identifier)
		self._tables[identifier] = table
		return table


	def tableClose(self, identifier):
		table = self._tables[identifier]
		table.close()
		del self._tables[identifier]


	def userAuth(self, username, password):
		"""Returns True if user may login, False otherwise."""
		if username not in self._accounts:  # User account does not exist.
			return False
		elif username in self._users:  # User already logged in.
			return False
		else:  # Check for correct password.
			return self._accounts[username]['password'] == password


	def userLogin(self, username, password, instance):
		"""Add instance."""
		if self.userAuth(username, password):
			self._users[username] = instance


	def userLogout(self, identifier):
		table = self.getUser(identifier).session['table']
		if table is not None:
			table.removePlayer(identifier)
		del self._users[identifier]


	def userRegister(self, username, password):
		"""Registers user in database."""
		if username in self._accounts:
			return False  # Username exists.
		else:
			self._accounts[username] = {
				'username' : username,
				'password' : password,
			}
			return True
