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

from pybridge.network.error import DeniedRequest, IllegalRequest


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
        
#        # Inform all observed tables.
 #       for table in self.tables.values():
  #          observer = table.observers[self]  # TODO
   #         table.stoppedObserving(self, observer)
        
        self.server.userDisconnects(self)  # Inform server.


    def callEvent(self, eventName, **kwargs):
        """Calls remote event listener with arguments."""
        if self.remote:
            self.remote.callRemote(eventName, **kwargs)


# Perspective methods, accessible by client.


    def perspective_getTables(self):
        """Provides RemoteTableManager to the client."""
        return self.server.tables


    def perspective_getUsers(self):
        """Provides RemoteUserManager to the client."""
        return self.server.users


    def perspective_hostTable(self, tableid):
        """Creates a new table."""
        if not isinstance(tableid, str):
            raise IllegalRequest, 'Invalid parameter for table identifier'
        elif not(0 < len(tableid) <= 20) or re.search("[^A-Za-z0-9_ ]", tableid):
            raise IllegalRequest, 'Invalid table identifier format'
        elif tableid in self.server.tables:
            raise DeniedRequest, 'Table name exists'
        
        self.server.createTable(tableid)
        return self.perspective_joinTable(tableid)  # Force join to table.


    def perspective_joinTable(self, tableid):
        """Joins an existing table."""
        if not isinstance(tableid, str):
            raise IllegalRequest, 'Invalid parameter for table name'
        elif tableid not in self.server.tables:
            raise DeniedRequest, 'No such table'
        elif tableid in self.tables:
            raise DeniedRequest, 'Already joined table'
        
        table = self.server.tables[tableid]
        self.tables[tableid] = table
        # Returning table reference creates a RemoteTable object on client.
        return table, table.view


    def perspective_leaveTable(self, tableid):
        """Leaves a table."""
        if not isinstance(tableid, str):
            raise IllegalRequest, 'Invalid parameter for table name'
        elif tableid not in self.tables:
            raise DeniedRequest, 'Not joined to table'
        
        table = self.tables[tableid]
        observer = table.observers[self]  # TODO
        del self.tables[tableid]




class AnonymousUser(pb.Avatar):


    def perspective_register(self, username, password):
        """Register a user account with given username and password."""
        if not isinstance(username, str):
            raise IllegalRequest, 'Invalid parameter for user name'
        elif not isinstance(password, str):
            raise IllegalRequest, 'Invalid parameter for password'
        
        self.server.userRegister(username, password)

