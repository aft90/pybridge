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

from database import database


class Checker:
	""""""

	__implements__ = checkers.ICredentialsChecker

	credentialInterfaces = (credentials.IUsernamePassword,
	                        credentials.IUsernameHashedPassword)


	def __init__(self):
		self.database = database


	def requestAvatarId(self, credentials):
		
		def gotUser(user):
			password = user.get('password')
			if password:
				d = defer.maybeDeferred(credentials.checkPassword, password)
				d.addCallback(passwordMatch)
				return d
			else:
				return unauthorized(None)
		
		def passwordMatch(matched):
			if matched:
				return credentials.username
			else:
				return unauthorized(None)
		
		def unauthorized(f):
			log.msg('Login failed for user %s' % credentials.username)
			return failure.Failure(error.UnauthorizedLogin())
		
		if credentials.username == '':
			return checkers.ANONYMOUS
		else:
			d = self.database.getUser(credentials.username)
			d.addCallback(gotUser)
			d.addErrback(unauthorized)
			return d

