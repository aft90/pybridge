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
from wrapper import WidgetWrapper
from lib.core.enumeration import CallType, Denomination, Seat


class WindowCalls(WidgetWrapper):

	widget_name = 'window_calls'


	def new(self):
		self.call_store = gtk.ListStore(str, str, str, str)
		self.call_tree.set_model(self.call_store)

		# Build columns.
		renderer = gtk.CellRendererText()
		for index, title in enumerate(Seat.Seats):
			column = gtk.TreeViewColumn(str.title(title), renderer, text=index)
			self.call_tree.append_column(column)

		# TEMP TEMP TEMP
		from lib.core.bidding import Call, Bidding
		x = Bidding(Seat.South)
		x.addCall(Call('pass'))
		x.addCall(Call('bid', 1, 'spade'))
		x.addCall(Call('bid', 1, 'notrump'))
		x.addCall(Call('bid', 2, 'club'))
		x.addCall(Call('bid', 2, 'diamond'))
		x.addCall(Call('bid', 4, 'spade'))
		x.addCall(Call('double'))
		x.addCall(Call('redouble'))
		x.addCall(Call('bid', 7, 'club'))
		x.addCall(Call('bid', 7, 'diamond'))
		x.addCall(Call('bid', 7, 'heart'))
		x.addCall(Call('bid', 7, 'spade'))
		x.addCall(Call('bid', 7, 'notrump'))
		x.addCall(Call('pass'))
		x.addCall(Call('pass'))
		x.addCall(Call('pass'))
		# TEMP TEMP TEMP.
		self.update_calls(x)


	def clear(self):
		self.call_store.clear()


	def update_calls(self, bidding):
		denom_symbols = {
			Denomination.Club    : u'\N{BLACK CLUB SUIT}',
			Denomination.Diamond : u'\N{BLACK DIAMOND SUIT}',
			Denomination.Heart   : u'\N{BLACK HEART SUIT}',
			Denomination.Spade   : u'\N{BLACK SPADE SUIT}',
			Denomination.NoTrump : u'NT'
		}
		type_symbols = {
			CallType.Pass     : 'pass',
			CallType.Double   : 'dbl',
			CallType.Redouble : 'rdbl'
		}

		self.clear()
		iter = self.call_store.append()  # Add first row.

		for call in bidding.calls:
			column = Seat.Seats.index(bidding.whoseCall(call))
			if column == 0:
				iter = self.call_store.append()  # Add new row.

			if call.callType is CallType.Bid:
				format = "%s%s" % (call.bidLevel, denom_symbols[call.bidDenom])
			else:
				format = type_symbols[call.callType]

			self.call_store.set(iter, column, format)
