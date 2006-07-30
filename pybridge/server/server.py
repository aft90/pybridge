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


from twisted.python import log

from database import database
from pybridge.network.tablemanager import LocalTableManager
from pybridge.network.usermanager import LocalUserManager

from pybridge.network.localbridge import LocalBridgeTable


class Server:


    def __init__(self):
        self.tables = LocalTableManager()
        self.users = LocalUserManager()


    def userConnects(self, user):
        """"""
        self.users.userLoggedIn(user)
        log.msg("User %s connected" % user.name)


    def userDisconnects(self, user):
        """"""
        self.users.userLoggedOut(user)
        log.msg("User %s disconnected" % user.name)


# Methods invoked by user perspectives.


    def userRegister(self, username, password):
        """"""
        d = database.addUser(username, password=password)
        log.msg("New user %s registered" % username)
        return d


    def createTable(self, tableid):
        if tableid not in self.tables:
            table = LocalBridgeTable(tableid)
            table.id = tableid
            table.server = self
            self.tables.openTable(table)

