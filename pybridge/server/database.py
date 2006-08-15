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


import shelve, anydbm, dbhash
from twisted.internet import defer
from twisted.python import failure

from pybridge.environment import environment


class DuplicateError(Exception):
    pass

class UnknownError(Exception):
    pass


class UserDatabase:
    """A simple database of user accounts."""


    def __init__(self):
        # Open the database file.
        dbfile = environment.find_configfile('users.db')
        self.accounts = shelve.open(dbfile, 'c', writeback=True)


    def addUser(self, username, **attrs):
        """Adds a new user."""
        if self.accounts.has_key(username):
            f = failure.Failure(DuplicateError())
            return defer.fail(f)
        
        profile = attrs.copy()
        profile['username'] = username
        self.accounts[username] = profile
        
        return defer.succeed(username)


    def removeUser(self, username):
        """Removes an existing user."""
        if not self.accounts.has_key(username):
            f = failure.Failure(UnknownError())
            return defer.fail(f)
        
        del self.accounts[username]
        
        return defer.succeed(username)
        

    def updateUser(self, username, **attrs):
        """Updates attributes for an existing user."""
        if not self.accounts.has_key(username):
            f = failure.Failure(UnknownError())
            return defer.fail(f)
        
        self.accounts[username].update(attrs)
        
        return defer.succeed(username)


    def getUser(self, username):
        """Returns a dict of information for an existing user."""
        if not self.accounts.has_key(username):
            f = failure.Failure(UnknownError())
            return defer.fail(f)
        
        info = self.accounts[username]
        
        return defer.succeed(info)


database = UserDatabase()

