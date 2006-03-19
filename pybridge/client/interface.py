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


class IPybridgeClientListener(Interface):
	"""The IPybridgeClientListener interface provides the events to drive a
	client connected to a PyBridge server.
	"""


	def gameCallMade(self, seat, call):
		"""Called when seat makes a call in this game."""

	def gameCardPlayed(self, seat, card):
		"""Called when seat plays a card in this game."""

	def gameContract(self, contract):
		"""Called when game contract is known."""

	def gameResult(self, result):
		"""Called when game result is known."""

	def gameStarted(self):
		"""Called when game is started."""

	def loginFailure(self):
		"""Called when login failed."""

	def loginSuccess(self):
		"""Called when login is successful."""

	def playerJoins(self, player, seat):
		"""Called when a player joins table."""

	def playerLeaves(self, player):
		"""Called when a player leaves table."""

	def protocolFailure(self, version):
		"""Called when protocol verification has failed."""

	def protocolSuccess(self, version):
		"""Called when protocol verification has succeeded."""

	def tableOpened(self, tablename):
		"""Called when a table has been created."""

	def tableClosed(self, tablename):
		"""Called when a table has been closed."""

	def tableListing(self, tables):
		"""Called when a listing of tables has been provided."""

	def userJoinsTable(self, username, tablename):
		"""Called when a user joins a table."""

	def userLeavesTable(self, username, tablename):
		"""Called when a user leaves a table."""

	def userLoggedIn(self, username):
		"""Called when user logs in."""

	def userLoggedOut(self, username):
		"""Called when user logs out."""

	def userListing(self, tables):
		"""Called when a listing of users has been provided."""
