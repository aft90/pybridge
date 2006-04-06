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


from twisted.spread import pb

from windowmanager import windowmanager

# Enumerations.
from pybridge.common.deck import Seat


class ClientEvents(pb.Referenceable):

	__implements__ = ()


	def remote_messageReceived(self, type, sender, message):
		print "message " + message


	def remote_tableOpened(self, tablename):
		windowmanager.get('window_tablelisting').add_tables((tablename,))


	def remote_tableClosed(self, tablename):
		windowmanager.get('window_tablelisting').remove_tables((tablename,))


	def remote_userLoggedIn(self, username):
		print username + " connected"


	def remote_userLoggedOut(self, username):
		print username + " disconnected"


class TableEvents(pb.Referenceable):


	def __init__(self, tablename):
		self.tablename = tablename


	def remote_userJoins(self, username):
		print "%s joins this table" % username
#		if username == self.name:
#			windowmanager.get('window_main').join_table(tablename)


	def remote_userLeaves(self, username):
		print "%s leaves this table" % username
#		if username == self.name:
#			windowmanager.destroy('window_game')
#			windowmanager.get('window_main').leave_table(tablename)


	def remote_playerSits(self, username, seat):
		print "player %s sits %s" % (username, seat)
		seat = getattr(Seat, seat)
		windowmanager.get('window_game').player_sits(username, seat)


	def remote_playerStands(self, username, seat):
		print "player %s stands %s" % (username, seat)
		seat = getattr(Seat, seat)
		windowmanager.get('window_game').player_stands(username, seat)


# Game events.


	def remote_gameCallMade(self, seat, call):
		print seat, call


	def remote_gameCardPlayed(self, seat, card):
		print seat, card


	def remote_gameContract(self, contract):
		print contract


	def remote_gameEnded(self):
		print "ended"


	def remote_gameResult(self, result):
		print result


	def remote_gameStarted(self, dealer):
		#Game(dealer, deal, None, False, False)
		print "gamestarted %s" % dealer

