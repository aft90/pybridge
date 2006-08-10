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

from cardarea import CardArea
from eventhandler import eventhandler
import utils

from pybridge.bridge.call import Bid, Pass, Double, Redouble

# Enumerations.
from pybridge.bridge.call import Level, Strain
from pybridge.bridge.card import Rank
from pybridge.bridge.deck import Seat


SEATS = {Seat.North : 'north', Seat.East  : 'east',
         Seat.South : 'south', Seat.West  : 'west', }

CALLTYPE_SYMBOLS = {Pass : 'pass', Double : 'dbl', Redouble : 'rdbl', }

LEVEL_SYMBOLS = {Level.One : '1',  Level.Two : '2',  Level.Three : '3',
                 Level.Four : '4', Level.Five : '5', Level.Six : '6',
                 Level.Seven : '7', }

RANK_SYMBOLS = {Rank.Two : '2',   Rank.Three : '3', Rank.Four : '4',
                Rank.Five : '5',  Rank.Six : '6',   Rank.Seven : '7',
                Rank.Eight : '8', Rank.Nine : '9',  Rank.Ten : '10',
                Rank.Jack : 'J',  Rank.Queen : 'Q', Rank.King : 'K',
                Rank.Ace : 'A', }

STRAIN_SYMBOLS = {Strain.Club    : u'\N{BLACK CLUB SUIT}',
                  Strain.Diamond : u'\N{BLACK DIAMOND SUIT}',
                  Strain.Heart   : u'\N{BLACK HEART SUIT}',
                  Strain.Spade   : u'\N{BLACK SPADE SUIT}',
                  Strain.NoTrump : u'NT', }


class WindowBridgetable(GladeWrapper):

    glade_name = 'window_bridgetable'

    callbacks = ('observerAdded', 'observerRemoved', 'playerAdded',
                 'playerRemoved', 'gameStarted', 'gameFinished',
                 'gameCallMade', 'gameCardPlayed', 'gameHandRevealed',
                 'messageReceived')


    def new(self):
        self.children = utils.WindowManager()
        self.table = None  # Table currently displayed in window.
        
        # Set up "Take Seat" menu.
        items = {}
        menu = gtk.Menu()
        for seat in Seat:
            items[seat] = gtk.MenuItem(seat.key, True)
            items[seat].connect('activate', self.on_seat_activated, seat)
            items[seat].show()
            menu.append(items[seat])
        self.takeseat.set_menu(menu)
        self.takeseat_items = items
        
        # Set up CardArea widget.
        self.cardarea = CardArea()
        self.cardarea.on_card_clicked = self.on_card_clicked
        self.cardarea.set_size_request(640, 480)
        self.scrolled_cardarea.add_with_viewport(self.cardarea)
        self.cardarea.show()
        
        renderer = gtk.CellRendererText()
        
        # Set up bidding history and column display.
        self.call_store = gtk.ListStore(str, str, str, str)
        self.biddingview.set_model(self.call_store)
        for index, title in enumerate(Seat):
            column = gtk.TreeViewColumn(str(title), renderer, text=index)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_fixed_width(50)
            self.biddingview.append_column(column)
        
        # Set up trick history and column display.
        self.trick_store = gtk.ListStore(str, str, str, str)
        self.trickview.set_model(self.trick_store)
        for index, title in enumerate(Seat):
            column = gtk.TreeViewColumn(str(title), renderer, text=index)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_fixed_width(50)
            self.trickview.append_column(column)
        
        # Set up score sheet and column display.
        self.score_store = gtk.ListStore(str, str, str, str)
        self.scoresheet.set_model(self.score_store)
        for index, title in enumerate(['Contract', 'Made', 'N/S', 'E/W']):
            column = gtk.TreeViewColumn(title, renderer, text=index)
            self.scoresheet.append_column(column)
        
        # Set up observer listing.
        self.observer_store = gtk.ListStore(str)
        self.treeview_observers.set_model(self.observer_store)
        column = gtk.TreeViewColumn(None, renderer, text=0)
        self.observer_store.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.treeview_observers.append_column(column)
        
        eventhandler.registerCallbacksFor(self, self.callbacks)


    def cleanup(self):
        self.table = None  # Dereference table.
        # Close all child windows.
        for windowname in self.children.keys():
            self.children.close(windowname)


    def setTable(self, table):
        """Changes display to match the table specified.
        
        @param table: the (now) focal table.
        """
        self.table = table
        self.window.set_title('Table %s' % table.id)
        self.resetGame()
        
        if table.game:
            
            # Redraw hands and, if playing in progress, redraw trick.
            for position in table.game.deal:
                self.redrawHand(position)
            if table.game.playing:
                self.redrawTrick()
            self.setTurnIndicator()
            
            for call in table.game.bidding.calls:
                seat = table.game.bidding.whoCalled(call)
                self.addCall(call, seat)
            
            self.setDealer(table.dealer)
            self.setVuln(table.game.vulnNS, table.game.vulnEW)
            
            # If contract, set contract.
            if table.game.bidding.isComplete():
                contract = table.game.bidding.getContract()
                self.setContract(contract)
            
            # If playing, set trick counts.
            if table.game.playing:
                for seat, cards in table.game.playing.played.items():
                    for card in cards:
                        self.addCard(card, seat)
                self.setTrickCount(table.game.getTrickCount())
            
            # If user is a player and bidding in progress, open bidding box.
            if table.seated and not table.game.bidding.isComplete():
                self.children.open('window_bidbox', parent=self)
        
        # Initialise seat menu and player labels.
        for seat, player in table.players.items():
            available = player is None or seat == table.seated
            self.takeseat_items[seat].set_property('sensitive', available)
            if player:
                self.event_playerAdded(table, player, seat)
            else:  # Seat vacant.
                self.event_playerRemoved(table, None, seat)

        # Initialise observer listing.
        self.observer_store.clear()
        for observer in table.observers:
            self.event_observerAdded(table, observer)


    def resetGame(self):
        """Clears bidding history, contract, trick counts."""
        self.cardarea.clear()
        self.call_store.clear()   # Reset bidding history.
        self.trick_store.clear()  # Reset trick history.
        self.setContract(None)    # Reset contract.
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
            format = '%s%s' % (LEVEL_SYMBOLS[call.level],
                               STRAIN_SYMBOLS[call.strain])
        else:
            format = CALLTYPE_SYMBOLS[call.__class__]
        self.call_store.set(iter, column, format)


    def addCard(self, card, position):
        """"""
        column = position.index
        row = self.table.game.playing.played[position].index(card)
        
        if self.trick_store.get_iter_first() == None:
            self.trick_store.append()
        iter = self.trick_store.get_iter_first()
        for i in range(row):
            iter = self.trick_store.iter_next(iter)
            if iter is None:
                iter = self.trick_store.append()
        
        strain_equivalent = getattr(Strain, card.suit.key)  # TODO: clean up.
        format = '%s%s' % (STRAIN_SYMBOLS[strain_equivalent],
                           RANK_SYMBOLS[card.rank])
        self.trick_store.set(iter, column, format)


    def addScore(self, contract, made, score):
        textContract = self.getContractFormat(contract)
        textMade = '%s' % made
        if contract['declarer'] in (Seat.North, Seat.South) and score > 0 \
        or contract['declarer'] in (Seat.East, Seat.West) and score < 0:
            textNS, textEW = '%s' % abs(score), ''
        else:
            textNS, textEW = '', '%s' % abs(score)
        self.score_store.prepend([textContract, textMade, textNS, textEW])


    def redrawHand(self, position, all=False):
        """Redraws cards making up the hand at position.
        
        Cards played are filtered out and omitted from display.
        Unknown cards are displayed face down.
        
        @param position:
        @param all: If True, do not filter out cards played.
        """
        hand = self.table.game.deal[position]
        played = []
        if self.table.game.playing:
            played = self.table.game.playing.played[position]
        
        if hand:  # Own or known hand.
            if all is True:  # Show all cards.
                played = []
            self.cardarea.build_hand(position, hand, omit=played)
        else:  # Unknown hand: draw cards face down, use integer placeholders.
            cards = range(13)
            played = range(len(played))
            self.cardarea.build_hand(position, cards, facedown=True, omit=played)
        
        self.cardarea.draw_hand(position)


    def redrawTrick(self, trick=None):
        """Redraws trick.
        
        @param table:
        @param trick:
        """
        # TODO: this cannot be called until playing in progress
        # perhaps put a clear() method in cardarea?
        if trick is None:
            trick = self.table.game.playing.getCurrentTrick()
        
        self.cardarea.build_trick(trick)
        self.cardarea.draw_trick()


    def setTurnIndicator(self):
        """Sets the statusbar text to indicate which player is on turn."""
        turn = self.table.game and not self.table.game.isComplete() \
        and self.table.game.whoseTurn()
        
        context = self.statusbar.get_context_id('turn')
        self.statusbar.pop(context)
        if turn:
            text = "It is %s's turn" % str(turn)
            self.statusbar.push(context, text)


    def setContract(self, contract=None):
        """Sets the contract label from contract."""
        format = (contract and self.getContractFormat(contract)) or 'No contract'
        self.label_contract.set_property('sensitive', contract!=None)
        self.label_contract.set_markup('<span size="x-large">%s</span>' % format)


    def setDealer(self, dealer):
        self.label_dealer.set_markup('<b>%s</b>' % dealer)


    def setTrickCount(self, count=None):
        """Sets the trick counter labels for declarer and defence.
        
        @param count:
        """
        if count:
            declarer = count['declarerWon'], count['declarerNeeds']
            defence = count['defenceWon'], count['defenceNeeds']
        else:
            declarer = defence = (0, 0)
        
        self.frame_declarer.set_property('sensitive', count!=None)
        self.frame_defence.set_property('sensitive', count!=None)
        self.label_declarer.set_markup('<span size="x-large"><b>%s</b> (%s)</span>' % declarer)
        self.label_defence.set_markup('<span size="x-large"><b>%s</b> (%s)</span>' % defence)


    def setVuln(self, vulnNS, vulnEW):
        vuln = {(True, True)  : 'All',
                (True, False) : 'N/S',
                (False, True) : 'E/W',
                (False, False) : 'Love all', }
        self.label_vuln.set_markup('<b>%s</b>' % vuln[(vulnNS, vulnEW)])


# Registered event handlers.


    def event_observerAdded(self, table, observer):
        if table == self.table:
            self.observer_store.append([observer])


    def event_observerRemoved(self, table, observer):
        
        def func(model, path, iter, user_data):
            if model.get_value(iter, 0) in user_data:
                model.remove(iter)
                return True
        
        if table == self.table:
            self.observer_store.foreach(func, observer)


    def event_playerAdded(self, table, player, position):
        if table == self.table:
            # Disable menu item corresponding to position.
            widget = self.takeseat_items[position]
            widget.set_property('sensitive', False)
            # Set player label.
            label = getattr(self, 'label_%s' % SEATS[position])
            label.set_markup('<b>%s</b>' % player)
            
            # If all seats occupied, disable Take Seat.
            if len([p for p in table.players.values() if p is None]) == 0:
                self.takeseat.set_property('sensitive', False)


    def event_playerRemoved(self, table, player, position):
        if table == self.table:
            # Enable menu item corresponding to position.
            widget = self.takeseat_items[position]
            widget.set_property('sensitive', True)
            # Reset player label.
            label = getattr(self, 'label_%s' % SEATS[position])
            label.set_markup('<i>Vacant</i>')
            
            # If we are not seated, ensure Take Seat is enabled.
            if not table.seated:
                self.takeseat.set_property('sensitive', True)


    def event_gameStarted(self, table, dealer, vulnNS, vulnEW):
        if table == self.table:
            self.children.close('dialog_gameresult')
            self.resetGame()
            
            self.setTurnIndicator()
            self.setDealer(table.dealer)
            self.setVuln(table.game.vulnNS, table.game.vulnEW)
            
            for position in table.game.deal:
                self.redrawHand(position)
            if table.seated:
                self.children.open('window_bidbox', parent=self)


    def event_gameCallMade(self, table, call, position):
        if table == self.table:
            self.addCall(call, position)
            self.setTurnIndicator()
            if table.game.bidding.isComplete():
                self.children.close('window_bidbox')  # If playing.
                contract = table.game.bidding.getContract()
                self.setContract(contract)


    def event_gameCardPlayed(self, table, card, position):
        if table == self.table:
            self.addCard(card, position)
            self.setTurnIndicator()
            count = table.game.getTrickCount()
            self.setTrickCount(count)
            self.redrawTrick()
            self.redrawHand(position)


    def event_gameFinished(self, table):
        if table == self.table:
            
            for position in table.game.deal:
                self.redrawHand(position, all=True)
            self.setTurnIndicator()
            
            # Determine and display score in dialog box.
            contract = table.game.bidding.getContract()
            if contract:
                trickCount = table.game.getTrickCount()
                offset = trickCount['declarerWon'] - trickCount['required']
                score = table.game.score()
                self.addScore(contract, trickCount['declarerWon'], score)
                
                textContract = 'Contract %s' % self.getContractFormat(contract)
                textTrick = (offset > 0 and 'made by %s tricks' % offset) or \
                            (offset < 0 and 'failed by %s tricks' % abs(offset)) or \
                            'made exactly'
                textScore = 'Score %s points for ' % abs(score) + \
                            ((score >= 0 and 'declarer') or 'defence')
                
                message = '%s %s.\n\n%s.' % (textContract, textTrick, textScore)
            else:
                message = 'Bidding passed out.'
            
            dialog = self.children.open('dialog_gameresult', parent=self)
            dialog.setup(message)


    def event_gameHandRevealed(self, table, hand, position):
        if table == self.table:
            self.redrawHand(position)


    def event_messageReceived(self, table, message, sender, recipients):
        if table == self.table:
            buffer = self.chat_messagehistory.get_buffer()
            iter = buffer.get_end_iter()
            buffer.insert(iter, '%s: %s\n' % (sender, message))
            self.chat_messagehistory.scroll_to_iter(iter, 0)


# Utility methods.


    def getContractFormat(self, contract):
        """Returns a format string representing the contract.
        
        @param contract: a dict from bidding.getContract().
        """
        bidlevel = LEVEL_SYMBOLS[contract['bid'].level]
        bidstrain = STRAIN_SYMBOLS[contract['bid'].strain]
        double = ''
        if contract['redoubleBy']:
            double = CALLTYPE_SYMBOLS[Redouble]
        elif contract['doubleBy']:
            double = CALLTYPE_SYMBOLS[Double]
        declarer = contract['declarer']
        
        return "%s%s%s by %s" % (bidlevel, bidstrain, double, declarer)


# Signal handlers.


    def on_card_clicked(self, card, position):
#        if self.table.playing and self.table.whoseTurn() == position:
        d = self.table.gamePlayCard(card, position)
        d.addErrback(lambda _: True)  # Ignore any error.


    def on_seat_activated(self, widget, seat):
        
        def success(r):
            self.takeseat.set_property('sensitive', False)
            self.leaveseat.set_property('sensitive', True)
            # If game is running and bidding is active, open bidding box.
            if self.table.game and not self.table.game.bidding.isComplete():
                self.children.open('window_bidbox', parent=self)
        
        d = self.table.addPlayer(seat)  # Take seat.
        d.addCallback(success)


    def on_takeseat_clicked(self, widget, *args):
        # TODO: match user up with preferred partner.
        for seat, player in self.table.players.items():
            if player is None:  # Vacant.
                self.on_seat_activated(widget, seat)
                break


    def on_leaveseat_clicked(self, widget, *args):
        
        def success(r):
            self.takeseat.set_property('sensitive', True)
            self.leaveseat.set_property('sensitive', False)
            self.children.close('window_bidbox')  # If open.
        
        d = self.table.removePlayer()  # Leave seat.
        d.addCallback(success)


    def on_toggle_gameinfo_clicked(self, widget, *args):
        visible = self.toggle_gameinfo.get_active()
        self.gameinfo.set_property('visible', visible)


    def on_toggle_chat_clicked(self, widget, *args):
        visible = self.toggle_chat.get_active()
        self.chatbox.set_property('visible', visible)


    def on_toggle_fullscreen_clicked(self, widget, *args):
        if self.toggle_fullscreen.get_active():
            self.window.fullscreen()
        else:
            self.window.unfullscreen()


    def on_leavetable_clicked(self, widget, *args):
        d = self.parent.leaveTable(self.table.id)
        d.addCallback(lambda _: utils.windows.close(self.glade_name, instance=self))


    def on_chat_message_changed(self, widget, *args):
        sensitive = self.chat_message.get_text() != ''
        self.chat_send.set_property('sensitive', sensitive)


    def on_chat_send_clicked(self, widget, *args):
        message = self.chat_message.get_text()
        if message:  # Don't send a null message.
            self.chat_send.set_property('sensitive', False)
            self.chat_message.set_text('')  # Clear message.
            self.table.sendMessage(message)


    def on_window_delete_event(self, widget, *args):
        d = self.parent.leaveTable(self.table.id)
        d.addCallback(lambda _: utils.windows.close(self.glade_name, instance=self))
        return True  # Stops window deletion taking place.

