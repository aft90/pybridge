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

from connector import connector

from pybridge.common.call import Bid, Pass, Double, Redouble

# Enumerations.
from pybridge.common.call import Level, Strain
from pybridge.common.deck import Seat


SEATS = {Seat.North : 'button_north',
         Seat.East  : 'button_east',
         Seat.South : 'button_south',
         Seat.West  : 'button_west', }

CALLTYPE_SYMBOLS = {Pass : 'pass', Double : 'dbl', Redouble : 'rdbl', }

STRAIN_SYMBOLS = {Strain.Club    : u'\N{BLACK CLUB SUIT}',
                  Strain.Diamond : u'\N{BLACK DIAMOND SUIT}',
                  Strain.Heart   : u'\N{BLACK HEART SUIT}',
                  Strain.Spade   : u'\N{BLACK SPADE SUIT}',
                  Strain.NoTrump : u'NT', }


class WindowGame(GladeWrapper):

	glade_name = 'window_game'


	def new(self):
		self.playing = None
		self.players = dict.fromkeys(Seat, None)
		
		self.call_store = gtk.ListStore(str, str, str, str)  # Four seats.
		self.tree_bidding.set_model(self.call_store)
		
		# Build columns for bidding view.
		renderer = gtk.CellRendererText()
		for index, seat in enumerate(Seat):
			column = gtk.TreeViewColumn(str(seat), renderer, text=index)
			self.tree_bidding.append_column(column)


	def setup(self, tablename):
		self.tablename = tablename
		
		def setup_players(info):
			for seat, username in info['players'].items():
				seat = getattr(Seat, seat)
				getattr(self, SEATS[seat]).set_property('sensitive', username==None)
		
		connector.callServer('getTableInfo', tablename=tablename).addCallback(setup_players)


	def player_sits(self, username, seat):
		self.players[seat] = username
		button = getattr(self, SEATS[seat])
		button.set_property('sensitive', False)


	def player_stands(self, username, seat):
		self.players[seat] = None
		button = getattr(self, SEATS[seat])
		# If we are not a player, enable seat.
		button.set_property('sensitive', self.playing==None)


	def update_bidding(self, bidding):
		""""""
		# If not finished, take the last call and add it on.
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


	def on_seat_clicked(self, widget, *args):
		
		def seated(arg):  # Disable all seat buttons except the one clicked.
			self.playing = seat
			for buttonname in SEATS.values():
				button = getattr(self, buttonname)
				button.set_property('sensitive', button==widget)
		
		def unseated(arg):  # Enable all seat buttons that are not seated.
			self.playing = None
			for seat, buttonname in SEATS.items():
				button = getattr(self, buttonname)
				button.set_property('sensitive', self.players[seat]==None)
		
		if widget.get_active():
			seat = [k for k, v in SEATS.items() if v==widget.get_name()][0]
			connector.callTable('sitPlayer', seat=str(seat)).addCallback(seated)
		else:
			connector.callTable('standPlayer').addCallback(unseated)

