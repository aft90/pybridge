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


class Command:
	"""Protocol commands which may be issued by client."""

	HOST = 'host'
	LIST = 'list'

	PROTOCOL = 'protocol'
	QUIT = 'quit'
	SET_PASSWORD = 'password'
	USER_LOGIN = 'login'
	USER_LOGOUT = 'logout'
	USER_REGISTER = 'register'

	SET_PASSWORD = 'password'
	TALK_CHAT = 'chat'
	TALK_KIBITZ = 'kibitz'
	TALK_SHOUT = 'shout'
	TALK_TELL = 'tell'

	TABLE_OBSERVE = 'observe'
	TABLE_LEAVE = 'leave'
	PLAYER_SIT = 'sit'
	PLAYER_STAND = 'stand'

	GAME_HISTORY = 'history'
	GAME_WHOSETURN = 'turn'

	GAME_CLAIMACCEPT = 'accept'
	GAME_ALERT = 'alert'
	GAME_CALL = 'call'
	GAME_CLAIMMAKE = 'claim'
	GAME_CLAIMCONCEDE = 'concede'
	GAME_CLAIMDECLINE = 'decline'
	CLAIM_HAND = 'hand'
	GAME_PLAYCARD = 'play'


class CommandReply:
	"""Prefixes to reply messages issued by server in response to client command."""

	ACKNOWLEDGE = 'ok'
	DENIED = 'no'
	ILLEGAL = 'bad'
	RESPONSE = 'data'


class Error:
	"""Protocol errors issued by server in response to a denied or illegal command from client."""

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

	PROTOCOL_UNSUPPORTED = 'protocol version unsupported'

	TABLE_BADNAME = 'invalid tablename'
	TABLE_EXISTS = 'table already exists'
	TABLE_SEATOCCUPIED = 'seat occupied'
	TABLE_UNKNOWN = 'no such table'

	USER_BADNAME = 'invalid username'	
	USER_REGISTERED = 'username already registered'
	USER_UNKNOWN = 'no such user'


class Event:
	"""A correspondence between protocol status messages and IProtocolListener events."""

	GAME_CALLMADE = 'gameCallMade'
	GAME_CARDPLAYED = 'gameCardPlayed'
	GAME_CONTRACTAGREED = 'gameContract'
	GAME_ENDED = 'gameEnded'
	GAME_RESULTKNOWN = 'gameResult'
	GAME_STARTED = 'gameStarted'
	
	SERVER_SHUTDOWN = 'serverShutdown'

	TABLE_PLAYERSTANDS = 'tablePlayerStands'
	TABLE_PLAYERSITS = 'tablePlayerSits'
	TABLE_USERJOINS = 'tableUserJoins'
	TABLE_USERLEAVES = 'tableUserLeaves'
	TABLE_OPENED = 'tableOpened'
	TABLE_CLOSED = 'tableClosed'

	TALK_MESSAGE = 'messageReceived'

	USER_LOGGEDIN = 'userLoggedIn'
	USER_LOGGEDOUT = 'userLoggedOut'
