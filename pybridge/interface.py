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


# Correspondence between protocol commands and executing functions.
COMMANDS = {

	# Connection and session control.
	'login'    : 'cmdLogin',
	'logout'   : 'cmdLogout',
	'protocol' : 'cmdProtocol',
	'quit'     : 'cmdQuit',
	'register' : 'cmdRegister',

	# Server commands.
	'host'     : 'cmdTableHost',
	'list'     : 'cmdList',
	'password' : 'cmdPassword',
	'shout'    : 'cmdTalkShout',
	'tell'     : 'cmdTalkTell',

	# Table commands.
	'chat'     : 'cmdTalkChat,',
	'kibitz'   : 'cmdTalkKibitz',
	'observe'  : 'cmdTableObserve',
	'leave'    : 'cmdTableLeave',
	'sit'      : 'cmdTableSit',
	'stand'    : 'cmdTableStand',

	# Game commands.
	'history'  : 'cmdGameHistory',
	'turn'     : 'cmdGameTurn',

	# Game player commands.
	'accept'   : 'cmdGameClaimAccept',
	'alert'    : 'cmdGameAlert',
	'call'     : 'cmdGameCall',
	'claim'    : 'cmdGameClaimClaim',
	'concede'  : 'cmdGameClaimConcede',
	'decline'  : 'cmdGameClaimDecline',
	'hand'     : 'cmdGameHand',
	'play'     : 'cmdGamePlay',
	'retract'  : 'cmdGameClaimRetract',

}


# Correspondence between protocol status messages and IProtocolListener events.
STATUS = {
	
	# Server events.
	'table_opened'      : 'tableOpened',
	'table_closed'      : 'tableClosed',
	'user_joins_table'  : 'userJoinsTable',
	'user_leaves_table' : 'userLeavesTable',
	'user_loggedin'     : 'userLoggedIn',
	'user_loggedout'    : 'userLoggedOut',

	# In-table events.
	'player_joins'      : 'playerJoins',	# sits
	'player_leaves'     : 'playerLeaves',	# stands

	# Game events.
	'game_call_made'    : 'gameCallMade',
	'game_card_played'  : 'gameCardPlayed',
	'game_contract'     : 'gameContract',
	'game_result'       : 'gameResult',
	'game_started'      : 'gameStarted',

	'message_received'  : 'messageReceived',

}


class IProtocolListener(Interface):
	"""The IProtocolListener interface provides the events to drive a
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

	def messageReceived(self, sender, message):
		"""Called when a message is received from sender."""

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
