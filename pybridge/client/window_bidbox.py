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


import gtk
from wrapper import GladeWrapper

#from pybridge.common.bidding import Call
#from pybridge.common.enumeration import CallType, Denomination, Level


#LEVELS = {'1' : Level.One, '2' : Level.Two, '3' : Level.Three, '4' : Level.Four, '5' : Level.Five, '6' : Level.Six, '7' : Level.Seven}

#DENOMS = {}


class WindowBidbox(GladeWrapper):

	glade_name = 'window_bidbox'


	def new(self):
		pass


	def update_from_bidding(self, bidding):
		"""Enables/disables call buttons based on bidding object."""
		pass


	def on_call_clicked(self, widget, *args):
		"""Builds a call object and submits."""
		calltext = widget.get_name()
		if calltext == 'pass':
			call = Call(CallType.Pass)
		elif calltext == 'double':
			call = Call(CallType.Double)
		elif calltext == 'redouble':
			call = Call(CallType.Redouble)
		else:  # Call is a bid, and calltext starts with 'bid'.
			bidLevel = int(calltext[3])
			bidDenom = None
		
		print widget, args
