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
from pybridge import __version__ as version

from pybridge.network.error import DeniedRequest, IllegalRequest
from pybridge.network.localtable import LocalTable
from pybridge.network.tablemanager import LocalTableManager
from pybridge.network.usermanager import LocalUserManager

from pybridge.bridge.game import BridgeGame


availableTables = LocalTableManager()
onlineUsers = LocalUserManager()


def getServerInfo():
    return {'supported': (version, version),  # minimum, maximum
            'version': version}


# Methods invoked by user perspectives.


def registerUser(username, password):
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


def changePasswordOfUser(username, password):
    """Sets the password of user to specified password.
    
    @param username: the user identifier.
    @param password: the new password for user.
    """
    pass  # TODO implement


def createTable(tableid, gametype):
    """Create a new table for the specified game type.
    
    @param tableid: a unique identifier for the table.
    @param gametype: a game identifier.
    """
    # TODO: convert gametype string to corresponding class.
    if tableid not in availableTables:
        table = LocalTable(tableid, BridgeGame)  # Ignore gametype for now.
        # Provide table instance with a means of closing itself.
        table.close = lambda: availableTables.closeTable(table)
        availableTables.openTable(table)

