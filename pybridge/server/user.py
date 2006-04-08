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


import re
from twisted.spread import pb

from database import database
from pybridge.enum import Enum
from pybridge.failure import *


class User(pb.Avatar):


	def __init__(self, name):
		self.name = name  # User name.
		self.server = None  # Set by Realm.
		self.tables = {}  # For each joined table name, its instance.


	def attached(self, mind):
		"""Called when connection to client is established."""
		self.remote = mind
		self.server.userConnects(self)


	def detached(self, mind):
		"""Called when connection to client is lost."""
		self.remote = None
		
		# Inform all observed tables.
		for table in self.tables.values():
			table.removeObserver(self.name)
		
		self.server.userDisconnects(self)  # Inform server.


	def callEvent(self, eventName, **kwargs):
                """Calls remote event listener with arguments."""
		if self.remote:
			self.remote.callRemote(eventName, **kwargs)


# Perspective methods, accessible by client.


	def perspective_getTables(self):
		"""Returns a dict of table instances, keyed by table name."""
		return self.tables


	def perspective_hostTable(self, tablename, listener):
		"""Creates a new table."""
		if not isinstance(tablename, str):
			raise InvalidParameterError()
		elif not(0 < len(tablename) <= 20) or re.search("[^A-Za-z0-9_ ]", tablename):
			raise IllegalNameError()
		elif tablename in self.server.tables:
			raise TableNameExistsError()
		
		self.server.tableOpen(tablename)
		return self.perspective_joinTable(tablename, listener)  # Force join.


	def perspective_joinTable(self, tablename, listener):
		"""Joins an existing table."""
		if not isinstance(tablename, str):
			raise IllegalParameterError()
		elif tablename not in self.server.tables:
			raise TableNameUnknownError()
		elif tablename in self.tables:  # Already watching table.
			raise TableObservingError()
		
		table = self.server.tables[tablename]
		table.addObserver(self.name, listener)
		self.tables[tablename] = table
		return table  # Reference to pb.Viewable table object.


	def perspective_leaveTable(self, tablename):
		"""Leaves a table."""
		if not isinstance(tablename, str):
			raise IllegalParameterError()
		elif tablename not in self.tables:  # Not watching table.
			raise TableObservingError()
		
		table = self.tables[tablename]
		table.removeObserver(self.name)
		del self.tables[tablename]


	def perspective_listTables(self):
		return self.server.tables.keys()


class AnonymousUser(pb.Avatar):


	def perspective_register(self, username, password):
		"""Register a user account with given username and password."""
		if not isinstance(username, str):
			raise IllegalParameterError()
		elif not isinstance(password, str):
			raise IllegalParameterError()
		# TODO: should this be mediated through the server?
		return database.addUser(username, password=password)

