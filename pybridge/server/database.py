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


import os, re
from datetime import datetime
from sqlobject import *
from sqlobject.inheritance import InheritableSQLObject

import pybridge.environment as env
from pybridge.bridge.deck import Seat


backend = "sqlite"

# Initiate connection to the appropriate database backend.
if backend == "sqlite":
    db_filename = env.find_config_server("pybridge-server.db")
    connection_string = "sqlite://" + db_filename # TODO: fix for Win32.

connection = connectionForURI(connection_string)
sqlhub.processConnection = connection  # Set all classes to use connection.


class UserAccount(SQLObject):
    """A store of user information.
    
    A user account is created when a user is registered.
    """

    username = StringCol(length=20, notNone=True, unique=True, alternateID=True)
    password = StringCol(length=40, notNone=True)  # Store SHA-1 hex hashes.
    allowLogin = BoolCol(default=True)  # If False, account login is disabled.
    email = StringCol(default=None, length=320)  # See RFC 2821 section 4.5.3.1.
    realname = UnicodeCol(default=None, length=40)
    profile = UnicodeCol(default=None)
    created = DateTimeCol(default=datetime.now)
    lastLogin = DateTimeCol(default=None)
    # friends = MultipleJoin('UserFriend', joinColumn='from_user')

    def _set_username(self, value):
        if not isinstance(value, str) or not(1 <= len(value) <= 20):
            raise ValueError, "Invalid specification of username"
        if re.search("[^A-z0-9_]", value):
            raise ValueError, "Username can only contain alphanumeric characters"
        self._SO_set_username(value)

    def _set_password(self, value):
        if not isinstance(value, str) or not(1 <= len(value) <= 40):
            raise ValueError, "Invalid specification of password"
        self._SO_set_password(value)

    def _set_email(self, value):
        # This regexp matches virtually all well-formatted email addresses.
        if value and not re.match("^[A-z0-9_.+-]+@([A-z0-9-]+\.)+[A-z]{2,6}$", value):
            raise ValueError, "Invalid or ill-formatted email address"
        self._SO_set_email(value)


for table in [UserAccount]:
    table.createTable(ifNotExists=True)


# The following tables are not used by PyBridge 0.3.
# They will be enhanced and used in future releases.


class UserFriend(SQLObject):
    """Models the social interconnections that exist between users.
    
    Client software may use this information to provide visual clues to users
    that members of their "social circle" are online.
    
    Users may specify the nature of their relationships: this takes inspiration
    from the XFN (XHTML Friend Network) model: see http://gmpg.org/xfn/. The
    symmetry arising from some types of relationship is eschewed for simplicity.
    
    This relation is irreflexive: no user can form a friendship with themselves!
    """

    fromUser = ForeignKey('UserAccount')  # The creator of the relationship.
    toUser = ForeignKey('UserAccount')  # The subject of the relationship.
    fromToIndex = DatabaseIndex('fromUser', 'toUser', unique=True)

    # XFN attributes.
    friendship = EnumCol(default=None, enumValues=['friend', 'acquaintance', 'contact'])
    physical = BoolCol(default=False)  # Having met in person.
    professional = EnumCol(default=None, enumValues=['co-worker', 'colleague'])
    geographical = EnumCol(default=None, enumValues=['co-resident', 'neighbour'])
    family = EnumCol(default=None, enumValues=['child', 'parent', 'sibling', 'spouse', 'kin'])
    romantic = EnumCol(default=None, enumValues=['muse', 'crush', 'date', 'sweetheart'])


class Game(InheritableSQLObject):
    """Captures game attributes common to all games.
    
    Implementations of specific games should inherit from this class.
    """

    start = DateTimeCol()
    complete = DateTimeCol()


class BridgeGame(Game):
    """Captures game attributes specific to bridge games.
    
    """
    
    board = ForeignKey('BridgeBoard')

    declarer = EnumCol(enumValues=list(Seat))
#    contract = 
    trickCount = IntCol()  # Number of tricks won by 
    score = IntCol()

    # Although key attributes of games are stored in fields (for searching),
    # the complete game is represented in PBN format.
    pbn = StringCol()

    # Players: no player may occupy more than one position.
    north = ForeignKey('UserAccount')
    east = ForeignKey('UserAccount')
    south = ForeignKey('UserAccount')
    west = ForeignKey('UserAccount')


class BridgeBoard(SQLObject):
    """Encapsulates the attributes which may be common to multiple bridge games.
    
    Separating board attributes from . 
    """

    deal = IntCol()
    dealer = EnumCol(enumValues=list(Seat))
    vuln = EnumCol(enumValues=['none', 'ns', 'ew', 'all'])

