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


from pybridge.interface import IProtocolListener
from pybridge.strings import Event


class ProtocolEvents:

	__implements__ = (IProtocolListener,)


# Game events.

	def gameCallMade(self, seat, call):
		self.sendStatus(Event.GAME_CALLMADE, "%s by %s" % (call, seat))

	def gameCardPlayed(self, seat, card):
		self.sendStatus(Event.GAME_CARDPLAYED, "%s by %s" % (card, seat))

	def gameContract(self, contract):
		if contract['redoubleBy']:
			doubled = " rdbl"
		elif contract['doubleBy']:
			doubled = " dbl"
		else:
			doubled = ""
		format = (contract['bid'], doubled, contract['declarer'])
		self.sendStatus(Event.GAME_CONTRACTAGREED, "%s%s by %s" % format)

	def gameEnded(self):
		self.sendStatus(Event.GAME_ENDED)

	def gameResult(self, result):
		self.sendStatus(Event.GAME_RESULTKNOWN, result)

	def gameStarted(self):
		self.sendStatus(Event.GAME_STARTED)

# Server events.

	def messageReceived(self, sender, message):
		self.sendStatus(Event.TALK_MESSAGE, sender, message)

	def serverShutdown(self):
		self.sendStatus(Event.SERVER_SHUTDOWN)

# Table events.

	def tablePlayerSits(self, player, seat):
		self.sendStatus(Event.TABLE_PLAYERSITS, player, seat)

	def tablePlayerStands(self, player):
		self.sendStatus(Event.TABLE_PLAYERSTANDS, player)

	def tableUserJoins(self, username, tablename):
		self.sendStatus(Event.TABLE_USERJOINS, username, tablename)

	def tableUserLeaves(self, username, tablename):
		self.sendStatus(Event.TABLE_USERLEAVES, username, tablename)

	def tableOpened(self, tablename):
		self.sendStatus(Event.TABLE_OPENED, tablename)

	def tableClosed(self, tablename):
		self.sendStatus(Event.TABLE_CLOSED, tablename)

# User events.

	def userLoggedIn(self, username):
		self.sendStatus(Event.USER_LOGGEDIN, username)

	def userLoggedOut(self, username):
		self.sendStatus(Event.USER_LOGGEDOUT, username)
