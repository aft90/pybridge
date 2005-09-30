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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from twisted.python.components import Interface


class ITableListener(Interface):
	"""The ITableListener interface allows monitoring of a table."""

	def gameCallMade(self, player, call):
		"""Called when player makes a call in this game."""

	def gameCardPlayed(self, player, card):
		"""Called when player plays a card in this game."""

	def gameContract(self):
		"""Called when game contract is known."""

	def gameResult(self, result):
		"""Called when game result is known."""

	def playerJoins(self, person, seat):
		"""Called when a player joins this table."""

	def playerLeaves(self, person):
		"""Called when a player leaves this table."""
