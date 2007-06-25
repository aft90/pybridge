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
from twisted.python import log

from config import config
from pybridge import environment as env


# Initiate connection to the appropriate database backend.
# See http://sqlobject.org/SQLObject.html#declaring-the-class

# This code has been tested with the SQLite database backend. If you experience
# problems with databases supported by SQLObject, please file a bug report.

engine = config['Database'].get('Engine', 'sqlite')  # Default to SQLite.

if engine == 'sqlite':
    dbpath = config['Database'].get('DatabaseName',
                                env.find_config_server('pybridge-server.db'))
    # SQLObject uses a special syntax to specify path on Windows systems.
    # This code block is from http://simpleweb.essienitaessien.com/example
    if(dbpath[1] == ':'): 
        s = re.sub('\\\\', '/', dbpath)  # Change '\' to '/'
	s = re.sub(':', '|', s, 1)  # Special for sqlite
	dbpath = '/' + s

    connection_string = "sqlite://" + dbpath

else:
    username = config['Database'].get('Username', '')
    password = config['Database'].get('Password', '')
    host = config['Database'].get('Host', 'localhost')
    port = config['Database'].get('Port', '')
    dbname = config['Database'].get('DatabaseName', 'pybridge')

    # Standard URI syntax (from http://sqlobject.org/SQLObject.html):
    # scheme://[user[:password]@]host[:port]/database[?parameters]
    connection_string = engine + '://'
    if username:
        connection_string += username
        if password:
            connection_string += ':' + password
        connection_string += '@'
    connection_string += host
    if port:
        connection_string += ':' + str(port)
    connection_string += '/' + dbname

try:
    connection = connectionForURI(connection_string)
    log.msg("Connection to %s database succeeded" % engine)
except Exception, e:
    log.err(e)
    log.msg("Could not connect to %s database with URI: %s"
            % (engine, connection_string))
    log.msg("Please check configuration file.")
    raise SystemExit  # Database connection is required for server operation.

sqlhub.processConnection = connection  # Set all SQLObjects to use connection.


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
            raise ValueError, "Username may only be alphanumeric characters"
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


'''

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

    declarer = EnumCol(enumValues=list(Player))
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
    dealer = EnumCol(enumValues=list(Direction))
    vuln = EnumCol(enumValues=list(Vulnerable))

'''

