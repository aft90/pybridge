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


import re
from twisted.python import log

from . import database as db
from pybridge import __version__ as SERVER_VERSION
from pybridge.games import SUPPORTED_GAMES

from pybridge.network.error import DeniedRequest, IllegalRequest
from pybridge.network.localtable import LocalTable
from pybridge.network.tablemanager import LocalTableManager
from pybridge.network.usermanager import LocalUserManager


availableTables = LocalTableManager()
onlineUsers = LocalUserManager()


# Information about this server, for relay to clients.
publicData = { 'supportedGames': list(SUPPORTED_GAMES.keys())
             , 'version': SERVER_VERSION
             }


def registerUser(username, password):
    """Registers a new user account in the database.
    
    @param username: the unique username requested by user.
    @param password: the password to be associated with the account.
    """
    # Check that username has not already been registered.
    if db.UserAccount.selectBy(username=username).count() > 0:
        raise DeniedRequest("Username already registered")

    # Create user account - may raise ValueError.
    db.UserAccount(username=username, password=password, allowLogin=True)
    log.msg("New user %s registered" % username)


def setUserPassword(username, password):
    """Changes the password of user's account.
    
    @param username: the user identifier.
    @param password: the new password for user.
    """
    try:
        user = db.UserAccount.selectBy(username=username)[0]
        user.set(password=password)  # May raise ValueError.
    except IndexError:
        raise DeniedRequest("User account does not exist")


def createTable(tableid, gamename, **tableOptions):
    """Create a new table for the specified game type.
    
    @param tableid: a unique identifier for the table.
    @param gamename: a game class identifier.
    @param tableOptions: optional parameters for table initialisation.
    """
    # TODO: convert gametype string to corresponding class.

    if not 0 < len(tableid) <= 20 or re.search("[^A-Za-z0-9_ ]", tableid):
        raise IllegalRequest("Invalid table identifier format")
    if tableid in availableTables:
        raise DeniedRequest("Table name exists")
    if gamename not in SUPPORTED_GAMES:
        raise DeniedRequest("Unsupported game class %s" % gamename)

    gameclass = SUPPORTED_GAMES[gamename]
    table = LocalTable(tableid, gameclass)
    # Provide table instance with a means of closing itself.
    table.close = lambda: availableTables.closeTable(table)
    availableTables.openTable(table)

    return table

