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

import database as db
from pybridge import __version__

from pybridge.network.error import DeniedRequest, IllegalRequest
from pybridge.network.localtable import LocalTable
from pybridge.network.tablemanager import LocalTableManager
from pybridge.network.usermanager import LocalUserManager

from pybridge.bridge.game import BridgeGame


class Server(object):


    def __init__(self):
        # Set up rosters.
        self.tables = LocalTableManager()
        self.users = LocalUserManager()

        self.version = __version__
        self.supported = ['bridge']


    def userConnects(self, user):
        """"""
        log.msg("User %s connected" % user.name)
        self.users.userLogin(user)
        db.UserAccount.byUsername(user.name).set(lastLogin=datetime.now())


    def userDisconnects(self, user):
        """"""
        log.msg("User %s disconnected" % user.name)
        self.users.userLogout(user)


# Methods invoked by user perspectives.


    def registerUser(self, username, password):
        """Registers a new user account in the database.
        
        @param username: the unique username requested by user.
        @param password: the password to be associated with the account.
        """
        # Check that username has not already been registered.
        if db.UserAccount.selectBy(username=username).count() > 0:
            raise DeniedRequest, "Username already registered"
        try:
            # Create user account.
            db.UserAccount(username=username, password=password, allowLogin=True)
            log.msg("New user %s registered" % username)
        except ValueError, err:
            raise IllegalRequest, err


    def userChangePassword(self, user, password):
        """"""
        pass


    def createTable(self, tableid, tabletype):
        # Ignore specified tabletype, for now.
        if tableid not in self.tables:
            table = LocalTable(tableid, BridgeGame)
            table.id = tableid
            table.server = self
            self.tables.openTable(table)
            #self.tables[tableid] = table

