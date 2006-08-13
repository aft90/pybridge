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


from twisted.cred import checkers, credentials, error
from twisted.internet import defer
from twisted.python import failure, log
from zope.interface import implements

from database import database


class Checker:
    """"""

    implements(checkers.ICredentialsChecker)

    credentialInterfaces = (credentials.IUsernamePassword,
                            credentials.IUsernameHashedPassword)


    def __init__(self):
        self.database = database
        self.users = {}  # Users online, from Server object.


    def requestAvatarId(self, credentials):
        
        def gotUser(user):
            password = user.get('password', '')
            d = defer.maybeDeferred(credentials.checkPassword, password)
            d.addCallback(passwordMatch)
            return d
        
        def passwordMatch(matched):
            if matched:
                if credentials.username in self.users.keys():
                    raise unauthorized('Already logged in')
                else:
                    return credentials.username
            else:
                return unauthorized('Incorrect password')
        
        def unauthorized(reason):
            log.msg('Login failed for %s: %s' % (credentials.username, reason))
            return failure.Failure(error.UnauthorizedLogin(reason))
        
        if credentials.username == '':
            return checkers.ANONYMOUS
        else:
            d = self.database.getUser(credentials.username)
            d.addCallbacks(gotUser, lambda e: unauthorized('No user account'))
            return d

