# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2007 PyBridge Project.
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
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from datetime import datetime
from twisted.python import log
from twisted.spread import pb

from pybridge.network.error import DeniedRequest, IllegalRequest

import database as db
import server


class RegisteredUser(pb.Avatar):

    info = property(lambda self: {})  # TODO: Send profile data?


    def __init__(self, name):
        self.name = name  # User name.

        self.accountRecord = db.UserAccount.byUsername(self.name)
        self.joinedTables = {}  # All tables which client is observing.


    def attached(self, mind):
        """Called when connection to client is established."""
        self.remote = mind
        self.accountRecord.set(lastLogin=datetime.now())
        server.onlineUsers.userLogin(self)  # Inform system of client's arrival.
        log.msg("User %s connected" % self.name)


    def detached(self, mind):
        """Called when connection to client is lost."""
        self.remote = None
        server.onlineUsers.userLogout(self)
        log.msg("User %s disconnected" % self.name)


# Perspective methods, accessible by client.


    def perspective_getServerInfo(self):
        """Provides a dict of information about the server."""
        return server.getServerInfo()


    def perspective_getRoster(self, name):
        """Provides roster requested by client."""
        if name == 'tables':
            return server.availableTables
        elif name == 'users':
            return server.onlineUsers
        else:
            raise DeniedRequest, "Unknown roster name \'%s\'" % name


    def perspective_getUserProfile(self, username):
        """Provides profile information for user with specified username."""
        pass


    def perspective_changePassword(self, password):
        """Sets avatar's user account password to that specified."""
        if not isinstance(password, str):
            raise IllegalRequest, "Invalid parameter for password"

        try:
            server.changeUserPassword(self.name, password)
        except ValueError, err:  # Password validation failed.
            raise DeniedRequest, err


    def perspective_hostTable(self, tableid, gametype):
        """Creates a new table."""
        if not isinstance(tableid, str):
            raise IllegalRequest, "Invalid parameter for table identifier"
        if not isinstance(gametype, str):
            raise IllegalRequest, "Invalid parameter for game type"
        
        table = server.createTable(tableid, gametype)
        # Force client to join table.
        return self.perspective_joinTable(tableid)


    def perspective_joinTable(self, tableid):
        """Joins an existing table."""
        if not isinstance(tableid, str):
            raise IllegalRequest, "Invalid parameter for table identifier"
        elif tableid not in server.availableTables:
            raise DeniedRequest, "No such table"
        elif tableid in self.joinedTables:
            raise DeniedRequest, "Already joined table"
        
        table = server.availableTables[tableid]
        self.joinedTables[tableid] = table
        return table


    def perspective_leaveTable(self, tableid):
        """Leaves a table."""
        if not isinstance(tableid, str):
            raise IllegalRequest, "Invalid parameter for table identifier"
        elif tableid not in self.joinedTables:
            raise DeniedRequest, "Not joined to table"
        
        del self.joinedTables[tableid]  # Implicitly removes user from table.




class AnonymousUser(pb.Avatar):


    def perspective_register(self, username, password):
        """Create a user account with specified username and password."""
        # TODO: consider defer.succeed, defer.fail, failure.Failure
        try:
            server.registerUser(username, password)
        except ValueError, err:  # Username/password validation failed.
            raise DeniedRequest, err
