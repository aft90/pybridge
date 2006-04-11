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

from connector import connector

from pybridge.common.call import Bid, Pass, Double, Redouble
from pybridge.common.call import Level, Strain

LEVEL_NAMES = {'1' : Level.One, '2' : Level.Two, '3' : Level.Three,
               '4' : Level.Four, '5' : Level.Five, '6' : Level.Six,
               '7' : Level.Seven, }

STRAIN_NAMES = {'club' : Strain.Club, 'diamond' : Strain.Diamond,
                'heart' : Strain.Heart, 'spade' : Strain.Spade,
                'nt' : Strain.NoTrump, }


class WindowBidbox(GladeWrapper):

	glade_name = 'window_bidbox'


	def new(self):
		pass


	def update_from_bidding(self, bidding):
		"""Enables/disables call buttons based on bidding object."""
		pass


	def on_call_clicked(self, widget, *args):
		"""Builds a call object and submits."""
		calltext = widget.get_name().replace("button_", "")
		
		if calltext == 'pass':
			call = Pass()
		elif calltext == 'double':
			call = Double()
		elif calltext == 'redouble':
			call = Redouble()
		else:  # Call is a bid, and calltext starts with 'bid'.
			level = LEVEL_NAMES[calltext[3]]
			strain = STRAIN_NAMES[calltext[4:]]
			call = Bid(level, strain)
		
		print call
		connector.table.makeCall(call)

