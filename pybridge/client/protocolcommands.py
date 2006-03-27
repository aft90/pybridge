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


from pybridge.conf import PYBRIDGE_PROTOCOL
from pybridge.strings import Command


class ProtocolCommands:
	# The callback=None parameter is a nasty way of implementing responses.
	# At some point, it will be replaced.


# Connection and session control.


	def cmdLogin(self, username, password, callback=None):
		self.sendCommand(Command.USER_LOGIN, callback, username, password)


	def cmdLogout(self, callback=None):
		self.sendCommand(Command.USER_LOGOUT, callback)


	def cmdProtocol(self, callback=None):
		self.sendCommand(Command.PROTOCOL, callback, PYBRIDGE_PROTOCOL)


	def cmdQuit(self, callback=None):
		self.sendCommand(Command.QUIT, callback)


	def cmdRegister(self, username, password, callback=None):
		self.sendCommand(Command.USER_REGISTER, callback, username, password)


# Server commands.


	def cmdHost(self, tablename, callback=None):
		self.sendCommand(Command.HOST, callback, tablename)


	def cmdList(self, request, callback=None):
		self.sendCommand(Command.LIST, callback, request)


# Table commands.


	def cmdLeave(self, callback=None):
		self.sendCommand(Command.TABLE_LEAVE, callback)


	def cmdObserve(self, tablename, callback=None):
		self.sendCommand(Command.TABLE_OBSERVE, callback, tablename)


	def cmdSit(self, tablename, seat, callback=None):
		self.sendCommand(Command.TABLE_SIT, callback, tablename, seat)


	def cmdStand(self, tablename, callback=None):
		self.sendCommand(Command.TABLE_STAND, callback, tablename)


# Game player commands.


	def cmdGameCall(self, callType, bidLevel=None, bidDenom=None, callback=None):
		self.sendCommand(Command.GAME_CALL, callback, callType, bidLevel, bidDenom)


	def cmdGameHand(self, seat=None, callback=None):
		self.sendCommand(Command.GAME_HAND, callback, seat)


	def cmdGamePlay(self, rank, suit, callback=None):
		self.sendCommand(Command.GAME_PLAY, callback, rank, suit)

