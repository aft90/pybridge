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

from pybridge.network.client import client
from eventhandler import eventhandler

from pybridge.bridge.call import Bid, Pass, Double, Redouble

# Enumerations.
from pybridge.bridge.call import Level, Strain
from pybridge.bridge.deck import Seat


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
        # Set up bidding view model.
        self.call_store = gtk.ListStore(str, str, str, str)  # 4 seats.
        self.tree_bidding.set_model(self.call_store)
        
        # Build columns for bidding view.
        renderer = gtk.CellRendererText()
        for index, seat in enumerate(Seat):
            column = gtk.TreeViewColumn(str(seat), renderer, text=index)
            self.tree_bidding.append_column(column)
        
        # Set up observer listing.
        self.observerlisting_store = gtk.ListStore(str)
        self.observerlisting.set_model(self.observerlisting_store)
        cell_renderer = gtk.CellRendererText()
        for index, title in enumerate( ('Name',) ):
            column = gtk.TreeViewColumn(title, cell_renderer, text=index)
            self.observerlisting.append_column(column)
        
        eventhandler.registerCallback('gameCallMade', self.gameCallMade)
        
        self.changeTable(self.parent.focalTable)
 #       self.reset_game()


    def changeTable(self, table):
        """Changes display to match the table specified.
        
        @param table: the (now) focal table.
        """
        self.call_store.clear()
        if table.game:
            for call in table.game.bidding.calls:
                seat = table.game.bidding.whoseCall(call)
                self.addCall(call, seat)
        
        if table.game and table.game.bidding.contract():
            contract = table.game.bidding.contract()
            self.set_contract(contract)
        else:  # Reset contract.
            self.frame_contract.set_property('sensitive', False)
            self.label_contract.set_markup('Not established')
        
        if table.game and table.game.playing:
            self.set_wontricks((1,2),(3,4)) # TODO
        else:  # Reset trick counts.
            self.frame_declarer.set_property('sensitive', False)
            self.label_declarer.set_markup('-')
            self.frame_defence.set_property('sensitive', False)
            self.label_defence.set_markup('-')

        # Initialise seat buttons.
        for seat, player in self.parent.focalTable.players.items():
            getattr(self, SEATS[seat]).set_property('sensitive', player==None)


#    def add_observers(self, observers):
#        """Adds specified observers to listing."""
#        for observername in observers:
#            row = (observername, )
#            iter = self.observerlisting_store.append(row)


#    def remove_observers(self, observers):
#        """Removes specified observers from listing."""
#        
#        def func(model, path, iter, user_data):
#            if model.get_value(iter, 0) in user_data:
#                model.remove(iter)
#            return True
#        
#        self.observerlisting_store.foreach(func, observers)


    def player_sits(self, username, seat):
        button = getattr(self, SEATS[seat])
        button.set_property('sensitive', False)


    def player_stands(self, username, seat):
        button = getattr(self, SEATS[seat])
        # If we are not a player, enable seat.
        button.set_property('sensitive', not(self.parent.focalTable.seated))


    def get_contract_format(self, contract):
        """Returns a format string representing the contract."""
        bidlevel = contract['bid'].level.index + 1
        bidstrain = STRAIN_SYMBOLS[contract['bid'].strain]
        double = ''
        if contract['redoubleBy']:
            double = CALLTYPE_SYMBOLS[Redouble]
        elif contract['doubleBy']:
            double = CALLTYPE_SYMBOLS[Double]
        declarer = contract['declarer']  # str?
        
        return "%s%s%s by %s" % (bidlevel, bidstrain, double, declarer)


    def reset_game(self):
        """Clears bidding history, contract, trick counts."""
        
        # Reset bidding.
        self.call_store.clear()
        
        # Reset contract.
        self.frame_contract.set_property('sensitive', False)
        self.label_contract.set_markup('Not established')
        
        # Reset trick counts.
        self.frame_declarer.set_property('sensitive', False)
        self.label_declarer.set_markup('-')
        self.frame_defence.set_property('sensitive', False)
        self.label_defence.set_markup('-')


    def gameCallMade(self, table, call, position):
        if table == self.parent.focalTable:
            self.addCall(call, position)


    def addCall(self, call, position):
        """Adds call from specified player, to bidding tab."""
        column = position.index
        if column == 0 or self.call_store.get_iter_first() == None:
            iter = self.call_store.append()
        else:  # Get bottom row. There must be a better way than this...
            iter = self.call_store.get_iter_first()
            while self.call_store.iter_next(iter) != None:
                iter = self.call_store.iter_next(iter)
        
        if isinstance(call, Bid):
            format = "%s%s" % (call.level.index+1, STRAIN_SYMBOLS[call.strain])
        else:
            format = CALLTYPE_SYMBOLS[call.__class__]
        self.call_store.set(iter, column, format)


    def set_contract(self, contract):
        """Sets the contract label from contract."""
        format = self.get_contract_format(contract)
        self.frame_contract.set_property('sensitive', True)
        self.label_contract.set_markup('<b>%s</b>' % format)


    def set_wontricks(self, declarer, defence):
        """Sets the trick counter labels for declarer and defence.
        
        declarer: (# obtained, # remaining to make contract)
        defence: (# obtained, # remaining to defeat contract)
        """
        self.frame_declarer.set_property('sensitive', True)
        self.label_declarer.set_markup('<b>%s (%s)</b>' % declarer)
        self.frame_defence.set_property('sensitive', True)
        self.label_defence.set_markup('<b>%s (%s)</b>' % defence)


    def set_result(self, contract, offset, score):
        if contract:
            contractformat = self.get_contract_format(contract)
            trickformat = ((offset > 0) and "made by %s tricks" % offset) or \
                          ((offset < 0 and "failed by %s tricks" % abs(offset))) or \
                          "made exactly"
            scoreformat = ("%s points for " % abs(score)) + \
                          (((score >= 0) and "declarer") or "defenders")
            message = "Contract %s %s.\n\nScore %s." % (contractformat, trickformat, scoreformat)
        else:
            message = "Bidding passed out."
            
        res = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL,
                                type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK,
                                message_format = message, )
        result_dialog.run()
        result_dialog.destroy()
        
#        # If playing, indicate readiness to start next game.
#        if client.table.seated:
#            client.table.setReadyFlag()


# Signal handlers.


    def on_seat_clicked(self, widget, *args):
        
        def seated(arg):  # Disable all seat buttons except the one clicked.
            for buttonname in SEATS.values():
                button = getattr(self, buttonname)
                button.set_property('sensitive', button==widget)
        
        def unseated(arg):  # Enable all seat buttons that are not seated.
            for seat, buttonname in SEATS.items():
                button = getattr(self, buttonname)
                button.set_property('sensitive', self.parent.focalTable.players[seat]==None)
        
        if widget.get_active():
            seat = [k for k, v in SEATS.items() if v==widget.get_name()][0]
            self.parent.focalTable.addPlayer(seat).addCallback(seated)
        else:
            self.parent.focalTable.removePlayer().addCallback(unseated)


    def on_window_game_delete_event(self, widget, *args):
        d = client.leaveTable(self.parent.focalTable.id)
        d.addCallback(lambda _: self.parent.leftTable(self.parent.focalTable))
        return True  # Stops window deletion taking place.
