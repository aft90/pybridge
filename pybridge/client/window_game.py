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


import gtk
from wrapper import GladeWrapper

from pybridge.common.call import Bid, Pass, Double, Redouble

# Enumerations.
from pybridge.common.call import Level, Strain
from pybridge.common.deck import Seat


CALLTYPE_SYMBOLS = {Pass : 'pass', Double : 'dbl', Redouble : 'rdbl', }

STRAIN_SYMBOLS = {Strain.Club    : u'\N{BLACK CLUB SUIT}',
                  Strain.Diamond : u'\N{BLACK DIAMOND SUIT}',
                  Strain.Heart   : u'\N{BLACK HEART SUIT}',
                  Strain.Spade   : u'\N{BLACK SPADE SUIT}',
                  Strain.NoTrump : u'NT', }


class WindowGame(GladeWrapper):

	glade_name = 'window_game'


	def new(self):
		self.call_store = gtk.ListStore(str, str, str, str)  # Four seats.
		self.tree_bidding.set_model(self.call_store)
		
		# Build columns.
		renderer = gtk.CellRendererText()
		for index, title in enumerate(Seat):
			column = gtk.TreeViewColumn(str(title), renderer, text=index)
			self.tree_bidding.append_column(column)
		
		# TEMP TEMP TEMP
		from pybridge.common.bidding import Bidding
		x = Bidding(Seat.West)
		x.addCall(Pass())
		x.addCall(Bid(Level.One, Strain.Spade))
		x.addCall(Bid(Level.One, Strain.NoTrump))
		x.addCall(Double())
		x.addCall(Redouble())
		x.addCall(Bid(Level.Three, Strain.Club))
		x.addCall(Double())
		x.addCall(Pass())
		x.addCall(Pass())
		x.addCall(Pass())
		# TEMP TEMP TEMP.
		self.update_bidding(x)


	def add_call(self, call):
		""""""
		pass


	def update_bidding(self, bidding):
		""""""
		
		self.call_store.clear()
		iter = self.call_store.append()  # Add first row.
		
		for call in bidding.calls:
			column = bidding.whoseCall(call).index
			if column == 0:
				iter = self.call_store.append()  # Add new row.
			
			if isinstance(call, Bid):
				format = "%s%s" % (call.level.index+1, STRAIN_SYMBOLS[call.strain])
			else:
				format = CALLTYPE_SYMBOLS[call.__class__]
			
			self.call_store.set(iter, column, format)


# Signal handlers.


	def on_window_game_delete_event(self, widget, *args):
		return True
