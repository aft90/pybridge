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

from table import BridgeTable


class Server:


	def __init__(self):
		self.tables = {}  # For each table name, its Table object.
		self.users = {}   # For each online user, its User instance.


	def userConnects(self, user):
		""""""
		self.users[user.name] = user
		self.informAllUsers('userLoggedIn', username=user.name)
		log.msg("User %s connected" % user.name)


	def userDisconnects(self, user):
		""""""
		del self.users[user.name]
		self.informAllUsers('userLoggedOut', username=user.name)
		log.msg("User %s disconnected" % user.name)


#  methods.


	def userTalk(self, talktype, sender, recipients, message):
		"""Sends message from sender to each recipient user."""
		# TODO: check silence lists.
		self.informUsers('messageReceived', recipients, type=talktype,
		                 sender=sender, message=message)


	def tableOpen(self, tablename):
		"""Creates and announces a new table."""
		if tablename not in self.tables:
			table = BridgeTable(tablename, self)  # Reference to server object.
			self.tables[tablename] = table
			self.informAllUsers('tableOpened', tablename=tablename)
			log.msg("Opened table \"%s\"" % tablename)


	def tableClose(self, tablename):
		"""Announces the closure of a table."""
		if tablename in self.tables:
			self.informAllUsers('tableClosed', tablename=tablename)
			del self.tables[tablename]
			log.msg("Closed table \"%s\"" % tablename)


# Utility functions.


	def informUsers(self, eventName, usernames, **kwargs):
		"""For each username, calls event handler with provided kwargs."""
		# Filter out users with lost connections.
		users = [self.users[name] for name in usernames if self.users[name].remote]
		for user in users:
			user.remote.callRemote(eventName, **kwargs)


	def informAllUsers(self, eventName, **kwargs):
		"""Same as informUsers, but informs all users."""
		self.informUsers(eventName, self.users.keys(), **kwargs)

