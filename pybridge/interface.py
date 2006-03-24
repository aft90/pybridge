# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2005 PyBridge Project.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA


from twisted.python.components import Interface


class IProtocolListener(Interface):
	"""The IProtocolListener interface provides the events to drive a
	client connected to a PyBridge server.
	"""

# Game events.

	def gameCallMade(self, seat, call):
		"""Called when seat makes a call in this game."""

	def gameCardPlayed(self, seat, card):
		"""Called when seat plays a card in this game."""

	def gameContract(self, contract):
		"""Called when game contract is known."""

	def gameEnded(self):
		"""Called when game has finished, or terminated abruptly."""

	def gameResult(self, result):
		"""Called when game result is known."""

	def gameStarted(self):
		"""Called when game is started."""

# Server events.

	def messageReceived(self, sender, message):
		"""Called when message is received from sender."""

	def serverShutdown(self):
		"""Called when server is in the process of shutting down."""

# Table events.

	def tablePlayerSits(self, player, seat):
		"""Called when a user occupies a seat at table, to become a player."""

	def tablePlayerStands(self, player):
		"""Called when a player relinquishes their seat at table."""

	def tableUserJoins(self, username, tablename):
		"""Called when a user joins a table."""

	def tableUserLeaves(self, username, tablename):
		"""Called when a user leaves a table."""

	def tableOpened(self, tablename):
		"""Called when a table has been created."""

	def tableClosed(self, tablename):
		"""Called when a table has been closed."""

# User events.

	def userLoggedIn(self, username):
		"""Called when a user logs in."""

	def userLoggedOut(self, username):
		"""Called when a user logs out."""
