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


from twisted.cred import checkers, credentials, error
from twisted.internet import defer
from twisted.python import failure, log
from zope.interface import implementer

from . import database as db
from . import server


@implementer(checkers.ICredentialsChecker)
class Checker:
    """A database-driven implementation of ICredentialsChecker."""


    credentialInterfaces = (credentials.IUsernamePassword,
                            credentials.IUsernameHashedPassword)


    def requestAvatarId(self, credentials):

        def unauthorized(reason):
            log.msg("Login failed for %s: %s" % (credentials.username, reason))
            return failure.Failure(error.UnauthorizedLogin(reason))

        def passwordMatch(matched):
            if matched:
                return credentials.username
            else:
                return unauthorized("Incorrect password for user")

        if credentials.username == '':
            return checkers.ANONYMOUS  # TODO: if allowAnonymousRegistration.

        userQuery = db.UserAccount.selectBy(username=credentials.username)
        if userQuery.count() == 0:
            return unauthorized("User account does not exist on server")
        elif userQuery[0].allowLogin is False:  # TODO: list index breaks on MySQL.
            return unauthorized("User account is disabled")
        elif credentials.username in server.onlineUsers:
            # TODO: delete old session and use this one instead?
            return unauthorized("User is already logged in")

        d = defer.maybeDeferred(credentials.checkPassword, userQuery[0].password)
        d.addCallback(passwordMatch)
        return d
 
