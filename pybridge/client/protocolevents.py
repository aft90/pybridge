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

from pybridge.common.bidding import Call
from pybridge.common.deck import Card
from pybridge.common.enumeration import CallType

from windowmanager import windowmanager


class ProtocolEvents:

	__implements__ = (IProtocolListener, )


	def gameCallMade(self, seat, call):
		components = split(call, ' ')
		callType = components[0]
		if callType == CallType.Bid:
			bidLevel, bidDenom = components[1:]
		else:
			bidLevel, bidDenom = None, None
		Call(callType, bidLevel, bidDenom)


	def gameCardPlayed(self, seat, card):
		print seat, card


	def gameContract(self, contract):
		pass


	def gameEnded(self):
		pass


	def gameResult(self, result):
		pass


	def gameStarted(self):
		pass


# Server events.


	def messageReceived(self, sender, message):
		pass

	def serverShutdown(self):
		pass


# Table events.


	def tablePlayerSits(self, player, seat):
		pass


	def tablePlayerStands(self, player):
		pass


	def tableUserJoins(self, username, tablename):
		if username == self.username:
			self.tablename = tablename
			print "meeeee"
		print "joined"


	def tableUserLeaves(self, username, tablename):
		pass


	def tableOpened(self, tablename):
		windowmanager.get('window_tablelisting').add_table(tablename)


	def tableClosed(self, tablename):
		windowmanager.get('window_tablelisting').remove_table(tablename)


# User events.


	def userLoggedIn(self, username):
		pass


	def userLoggedOut(self, username):
		pass

