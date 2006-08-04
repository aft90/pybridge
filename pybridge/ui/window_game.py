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
import utils

from pybridge.bridge.call import Bid, Pass, Double, Redouble

# Enumerations.
from pybridge.bridge.call import Level, Strain
from pybridge.bridge.deck import Seat


SEATS = {Seat.North : 'north', Seat.East  : 'east',
         Seat.South : 'south', Seat.West  : 'west', }

CALLTYPE_SYMBOLS = {Pass : 'pass', Double : 'dbl', Redouble : 'rdbl', }

STRAIN_SYMBOLS = {Strain.Club    : u'\N{BLACK CLUB SUIT}',
                  Strain.Diamond : u'\N{BLACK DIAMOND SUIT}',
                  Strain.Heart   : u'\N{BLACK HEART SUIT}',
                  Strain.Spade   : u'\N{BLACK SPADE SUIT}',
                  Strain.NoTrump : u'NT', }

CONTRACT_FORMAT = '<span size="x-large">%s</span>'
TRICKCOUNT_FORMAT = '<span size="x-large"><b>%s</b> (%s)</span>'


class WindowGame(GladeWrapper):

    glade_name = 'window_game'


    def new(self):
        self.table = None
        
        # Set up bidding view model.
        self.call_store = gtk.ListStore(str, str, str, str)  # 4 seats.
        self.treeview_bidding.set_model(self.call_store)
        
        # Build columns for bidding view.
        renderer = gtk.CellRendererText()
        for index, seat in enumerate(Seat):
            column = gtk.TreeViewColumn(str(seat), renderer, text=index)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_fixed_width(50)
            self.treeview_bidding.append_column(column)
        
#        # Set up observer listing.
#        self.observerlisting_store = gtk.ListStore(str)
#        self.observerlisting.set_model(self.observerlisting_store)
#        cell_renderer = gtk.CellRendererText()
#        for index, title in enumerate( ('Name',) ):
#            column = gtk.TreeViewColumn(title, cell_renderer, text=index)
#            self.observerlisting.append_column(column)
        
        eventhandler.registerCallback('playerAdded', self.event_playerAdded)
        eventhandler.registerCallback('playerRemoved', self.event_playerRemoved)
        eventhandler.registerCallback('gameCallMade', self.event_gameCallMade)
        eventhandler.registerCallback('gameCardPlayed', self.event_gameCardPlayed)
        eventhandler.registerCallback('gameStarted', self.event_gameStarted)
        eventhandler.registerCallback('gameFinished', self.event_gameFinished)


    def changeTable(self, table):
        """Changes display to match the table specified.
        
        @param table: the (now) focal table.
        """
        self.window.set_title('Table %s' % table.id)
        if table is not self.table:
            self.table = table
            # Rebuild bidding list.
            self.call_store.clear()
            if table.game:
                for call in table.game.bidding.calls:
                    seat = table.game.bidding.whoCalled(call)
                    self.addCall(call, seat)
            # Set contract.
            if table.game and table.game.bidding.isComplete():
                contract = table.game.bidding.getContract()
                self.setContract(contract)
            else:  # Reset contract.
                self.setContract()
            # Set trick counts.
            if table.game and table.game.playing:
                self.setTrickCount(table.game.getTrickCount())
            else:  # Reset trick counts.
                self.setTrickCount(None)
            
            # If user is a player and bidding in progress, open bidding box.
            if table.seated and not table.game.bidding.isComplete():
                utils.windows.open('window_bidbox', self)
            else:  # Otherwise, if bidding box is open, close it.
                utils.windows.close('window_bidbox')
        
        # Initialise seat buttons.
        for seat, player in table.players.items():
            button = getattr(self, 'button_%s' % SEATS[seat])
#            label = getattr(self, 'label_%s' % SEATS[seat])
            available = player is None or seat == table.seated
            button.set_property('sensitive', available)
#            label.set_text(player or 'Vacant')


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


    def resetGame(self):
        """Clears bidding history, contract, trick counts."""
        self.call_store.clear()  # Reset bidding.
        self.setContract(None)  # Reset contract.
        self.setTrickCount(None)  # Reset trick counts.


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
            format = '%s%s' % (call.level.index+1, STRAIN_SYMBOLS[call.strain])
        else:
            format = CALLTYPE_SYMBOLS[call.__class__]
        self.call_store.set(iter, column, format)


    def setContract(self, contract=None):
        """Sets the contract label from contract."""
        if contract:
            format = CONTRACT_FORMAT % self.getContractFormat(contract)
        else:
            format = CONTRACT_FORMAT % 'No contract'
        
        self.label_contract.set_property('sensitive', contract!=None)
        self.label_contract.set_markup(format)


    def setTrickCount(self, count=None):
        """Sets the trick counter labels for declarer and defence.
        
        @param count:
        """
        if count:
            declarer = TRICKCOUNT_FORMAT % (count['declarerWon'], count['declarerNeeds'])
            defence = TRICKCOUNT_FORMAT % (count['defenceWon'], count['defenceNeeds'])
        else:
            declarer = TRICKCOUNT_FORMAT % (0, 0)
            defence = declarer
        
        self.frame_declarer.set_property('sensitive', count!=None)
        self.frame_defence.set_property('sensitive', count!=None)
        self.label_declarer.set_markup(declarer)
        self.label_defence.set_markup(defence)


# Registered event handlers.


    def event_playerAdded(self, table, player, position):
        if table == self.table:
            button = getattr(self, 'button_%s' % SEATS[position])
            label = getattr(self, 'button_%s' % SEATS[position])
            # Disable the button, unless we are the player.
            button.set_property('sensitive', button.get_active())
            if table.seated and table.game and not table.game.bidding.isComplete():
                utils.windows.open('window_bidbox', self)


    def event_playerRemoved(self, table, player, position):
        if table == self.table:
            button = getattr(self, 'button_%s' % SEATS[position])
            label = getattr(self, 'button_%s' % SEATS[position])
            # If we are not a player, enable seat button.
            button.set_property('sensitive', not(table.seated))
            utils.windows.close('window_bidbox')


    def event_gameCallMade(self, table, call, position):
        if table == self.table:
            self.addCall(call, position)
            if table.game.bidding.isComplete():
                contract = table.game.bidding.getContract()
                self.setContract(contract)


    def event_gameCardPlayed(self, table, card, position):
        if table == self.table:
            count = table.game.getTrickCount()
            self.setTrickCount(count)


    def event_gameStarted(self, table, dealer, vulnNS, vulnEW):
        if table == self.table:
            utils.windows.close('dialog_gameresult')
            self.resetGame()
            if table.seated:
                utils.windows.open('window_bidbox', self)


    def event_gameFinished(self, table):
        if table == self.table:
            # Determine and display score in dialog box.
            contract = table.game.bidding.getContract()
            if contract:
                trickCount = table.game.getTrickCount()
                offset = trickCount['declarerWon'] - trickCount['required']
                score = table.game.score()
                
                textContract = 'Contract %s' % self.getContractFormat(contract)
                textTrick = (offset > 0 and 'made by %s tricks' % offset) or \
                            (offset < 0 and 'failed by %s tricks' % abs(offset)) or \
                            'made exactly'
                textScore = 'Score %s points for ' % abs(score) + \
                            ((score >= 0 and 'declarer') or 'defence')
                
                message = '%s %s.\n\n%s.' % (textContract, textTrick, textScore)
            else:
                message = 'Bidding passed out.'

            dialog = utils.windows.open('dialog_gameresult', self.parent)
            dialog.setup(message)


# Utility methods.


    def getContractFormat(self, contract):
        """Returns a format string representing the contract.
        
        @param contract: a dict from bidding.getContract().
        """
        bidlevel = contract['bid'].level.index + 1
        bidstrain = STRAIN_SYMBOLS[contract['bid'].strain]
        double = ''
        if contract['redoubleBy']:
            double = CALLTYPE_SYMBOLS[Redouble]
        elif contract['doubleBy']:
            double = CALLTYPE_SYMBOLS[Double]
        declarer = contract['declarer']
        
        return "%s%s%s by %s" % (bidlevel, bidstrain, double, declarer)


# Signal handlers.


    def on_seat_clicked(self, widget, *args):
        
        def seated(arg):  # Disable all seat buttons except the one clicked.
            for name in SEATS.values():
                button = getattr(self, 'button_%s' % name)
                button.set_property('sensitive', button==widget)
        
        def unseated(arg):  # Enable all seat buttons that are not seated.
            for seat, name in SEATS.items():
                button = getattr(self, 'button_%s' % name)
                button.set_property('sensitive', self.table.players[seat]==None)
        
        if widget.get_active():  # Sit.
            seat = [k for k, v in SEATS.items() if v==widget.get_name().split('_')[1]][0]
            self.table.addPlayer(seat).addCallback(seated)
        else:  # Stand.
            self.table.removePlayer().addCallback(unseated)


    def on_window_game_delete_event(self, widget, *args):
        d = client.leaveTable(self.table.id)
        d.addCallback(lambda _: self.parent.leftTable(self.table))
        return True  # Stops window deletion taking place.

