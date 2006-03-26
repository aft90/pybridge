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


import shlex
from twisted.protocols.basic import LineOnlyReceiver

from pybridge.conf import PYBRIDGE_PROTOCOL
from pybridge.strings import CommandReply, Error

from protocolcommands import ProtocolCommands
from protocolevents import ProtocolEvents


class PybridgeServerProtocol(LineOnlyReceiver, ProtocolCommands, ProtocolEvents):

	SUPPORTED_PROTOCOLS = (PYBRIDGE_PROTOCOL,)

	class Acknowledgement(Exception): pass
	class DeniedCommand(Exception): pass
	class IllegalCommand(Exception): pass
	class Response(Exception): pass


	def __init__(self):
		self.username = None
		self.table = None
		self.version = None  # Version of client protocol.


	def connectionMade(self):
		pass
		

	def connectionLost(self, reason):
		if self.username:
			self.factory.userLogout(self.username)


	def lineReceived(self, line):
		tag = '-'	# In case of no #-tag provided.
		try:
			
			# Extract tokens from line.
			try:
				tokens = shlex.split(line)
			except ValueError, error:
				raise self.IllegalCommand(Error.COMMAND_PARSE)
			
			# Check for a command.
			if len(tokens) == 0:
				raise self.IllegalCommand(Error.COMMAND_REQUIRED)
			elif len(tokens) == 1 and tokens[0].startswith('#'):
				tag = tokens[0]
				raise self.IllegalCommand(Error.COMMAND_REQUIRED)
			
			# Get tag, command and any supplied parameters.
			if tokens[0].startswith('#'):
				tag       = tokens[0]	# Tag provided.
				command   = tokens[1].capitalize()
				arguments = tokens[2:]
			else:
				command   = tokens[0].capitalize()
				arguments = tokens[1:]
			
			# Command verification.
			dispatcher = getattr(self, "cmd%s" % command, None)
			if dispatcher is None:
				raise self.IllegalCommand(Error.COMMAND_UNKNOWN)
			
			# Parameter count verification.
			argsMax = dispatcher.func_code.co_argcount - 1	# "self"
			argsMin = argsMax - len(dispatcher.func_defaults or [])
			if argsMin > len(arguments) or argsMax < len(arguments):
				raise self.IllegalCommand(Error.COMMAND_PARAMNUM)
			
			# Call command, and be ready to trap resultant exceptions.
			dispatcher(*arguments)	# Execution.
			raise self.Acknowledgement	# (If we get this far.)
		
		except self.Acknowledgement:
			self.sendReply(tag, CommandReply.ACKNOWLEDGE)
		except self.DeniedCommand, error:	# Command is irrelevant.
			self.sendReply(tag, CommandReply.DENIED, error)
		except self.IllegalCommand, error:	# Command is ill-formatted.
			self.sendReply(tag, CommandReply.ILLEGAL, error)
		except self.Response, tokens:
			self.sendReply(tag, CommandReply.RESPONSE, *tokens.args)


	def sendReply(self, tag, signal, *args):
		"""Sends reply message to client."""
		tokens = ["\'%s\'" % str(arg).strip() for arg in args]
		self.sendLine(str.join(' ', [tag, signal] + tokens))


	def sendStatus(self, event, *args):
		"""Sends status message to client."""
		tokens = ["\'%s\'" % str(arg).strip() for arg in args]
		self.sendLine(str.join(' ', ['*', event] + tokens))
