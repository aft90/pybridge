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
from pybridge.strings import Error

class DeniedRequest(pb.Error): pass
class IllegalRequest(pb.Error): pass


class User(pb.Avatar):

#	__implements__ = IPerspective


	def __init__(self, name):
		self.name = name  # User name.
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
		self.validateType(tablename, str)

		if tablename in self.server.tables:
			raise DeniedRequest(Error.TABLE_EXISTS)
		elif not(0 < len(tablename) <= 20) or re.search("[^A-Za-z0-9_ ]", tablename):
			raise DeniedRequest(Error.TABLE_BADNAME)
		
		self.server.tableOpen(tablename)
		return self.perspective_joinTable(tablename, listener)  # Force join.


	def perspective_joinTable(self, tablename, listener):
		"""Joins an existing table."""
		self.validateType(tablename, str)
		
		if tablename not in self.server.tables:
			raise DeniedRequest(Error.TABLE_UNKNOWN)
		elif tablename in self.tables:
			raise DeniedRequest()
		
		table = self.server.tables[tablename]
		table.addObserver(self.name, listener)
		self.tables[tablename] = table
		return table  # Reference to pb.Viewable table object.


	def perspective_leaveTable(self, tablename):
		"""Leaves a table."""
		self.validateType(tablename, str)
		
		if tablename not in self.tables:
			raise DeniedRequest()
		
		table = self.tables[tablename]
		table.removeObserver(self.name)
		del self.tables[tablename]


	def perspective_listTables(self):
		return self.server.tables.keys()


	def perspective_getTableInfo(self, tablename):
		"""Request information on the state of a specified table."""
		self.validateType(tablename, str)

		if tablename not in self.server.tables:
			raise DeniedRequest(Error.TABLE_UNKNOWN)
		
		table = self.server.tables[tablename]
		return {'players'   : [(str(k), v) for k, v in table.players.items()],
		        'observers' : table.observers.keys(),
		        'inGame'    : table.game != None, }


# Utility methods.


	def validateType(self, object, expected):
		"""Validates the type of a given parameter against what is expected."""
		if isinstance(object, expected) or object in expected:
			return
		else:
			raise IllegalRequest(Error.COMMAND_PARAMSPEC)



class AnonymousUser(pb.Avatar):

#	__implements__ = IPerspective


	def perspective_register(self, username, password):
		"""Register a user account with given username and password."""
		return database.addUser(username, password=password)

