# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2006 PyBridge Project.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not write to the Free Software
# Foundation Inc. 51 Franklin Street Fifth Floor Boston MA 02110-1301 USA.


class Error:
	"""Protocol errors issued by server in response to a denied or illegal request from client."""

	COMMAND_PARAMNUM = 'invalid number of parameters'
	COMMAND_PARAMSPEC = 'invalid parameter'
	COMMAND_PARSE = 'unable to parse'
	COMMAND_REQUIRED = 'command required'
	COMMAND_UNAVAILABLE = 'command unavailable'
	COMMAND_UNIMPLEMENTED = 'command not yet implemented'
	COMMAND_UNKNOWN = 'unknown command'

	GAME_INVALIDCALL = 'invalid call'
	GAME_INVALIDCARD = 'invalid card'
	GAME_OUTOFTURN = 'out of turn'
	GAME_UNAVAILABLE = 'unavailable'

	LOGIN_ALREADY = 'already logged in'
	LOGIN_BADPASSWORD = 'incorrect password'
	LOGIN_NOACCOUNT = 'not registered'

	TABLE_BADNAME = 'invalid tablename'
	TABLE_EXISTS = 'table already exists'
	TABLE_SEATOCCUPIED = 'seat occupied'
	TABLE_UNKNOWN = 'no such table'

	USER_BADNAME = 'invalid username'	
	USER_REGISTERED = 'username already registered'
	USER_UNKNOWN = 'no such user'

