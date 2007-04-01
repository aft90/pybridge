# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2007 PyBridge Project.
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
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import gtk
from wrapper import GladeWrapper

from cardarea import CardArea
from eventhandler import SimpleEventHandler
import utils
from pybridge.network.error import GameError
from pybridge.bridge.call import Bid, Pass, Double, Redouble
from pybridge.bridge.symbols import Direction, Level, Strain, Rank, Vulnerable


# Translatable symbols for elements of bridge.

CALLTYPE_SYMBOLS = {Pass : _('pass'), Double : _('dbl'), Redouble : _('rdbl') }

DIRECTION_SYMBOLS = {Direction.North : _('North'), Direction.East : _('East'),
                     Direction.South : _('South'), Direction.West : _('West') }

LEVEL_SYMBOLS = {Level.One : _('1'), Level.Two : _('2'), Level.Three : _('3'),
                 Level.Four : _('4'), Level.Five : _('5'), Level.Six : _('6'),
                 Level.Seven : _('7') }

RANK_SYMBOLS = {Rank.Two : _('2'),   Rank.Three : _('3'), Rank.Four : _('4'),
                Rank.Five : _('5'),  Rank.Six : _('6'),   Rank.Seven : _('7'),
                Rank.Eight : _('8'), Rank.Nine : _('9'),  Rank.Ten : _('10'),
                Rank.Jack : _('J'),  Rank.Queen : _('Q'), Rank.King : _('K'),
                Rank.Ace : _('A') }

STRAIN_SYMBOLS = {Strain.Club    : u'\N{BLACK CLUB SUIT}',
                  Strain.Diamond : u'\N{BLACK DIAMOND SUIT}',
                  Strain.Heart   : u'\N{BLACK HEART SUIT}',
                  Strain.Spade   : u'\N{BLACK SPADE SUIT}',
                  Strain.NoTrump : u'NT' }

VULN_SYMBOLS = {Vulnerable.All : _('All'), Vulnerable.NorthSouth : _('N/S'),
                Vulnerable.EastWest : _('E/W'), Vulnerable.None : _('None') }


class WindowBridgetable(GladeWrapper):

    glade_name = 'window_bridgetable'


    def new(self):
        self.children = utils.WindowManager()
        self.eventHandler = SimpleEventHandler(self)

        self.table = None  # Table currently displayed in window.
        self.handler = None
        self.player, self.position = None, None

        # Set up "Take Seat" menu.
        self.takeseat_items = {}
        menu = gtk.Menu()
        for position in Direction:
            item = gtk.MenuItem(DIRECTION_SYMBOLS[position], True)
            item.connect('activate', self.on_seat_activated, position)
            item.show()
            menu.append(item)
            self.takeseat_items[position] = item
        self.takeseat.set_menu(menu)

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
        for index, position in enumerate(Direction):
            title = DIRECTION_SYMBOLS[position]
            column = gtk.TreeViewColumn(str(title), renderer, text=index)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_fixed_width(50)
            self.biddingview.append_column(column)

        # Set up trick history and column display.
        self.trick_store = gtk.ListStore(str, str, str, str)
        self.trickview.set_model(self.trick_store)
        for index, position in enumerate(Direction):
            title = DIRECTION_SYMBOLS[position]
            column = gtk.TreeViewColumn(str(title), renderer, text=index)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_fixed_width(50)
            self.trickview.append_column(column)

        # Set up score sheet and column display.
        self.score_store = gtk.ListStore(str, str, str, str)
        self.scoresheet.set_model(self.score_store)
        for index, title in enumerate([_('Contract'), _('Made'), _('N/S'), _('E/W')]):
            column = gtk.TreeViewColumn(title, renderer, text=index)
            self.scoresheet.append_column(column)

        # Set up observer listing.
        self.observer_store = gtk.ListStore(str)
        self.treeview_observers.set_model(self.observer_store)
        column = gtk.TreeViewColumn(None, renderer, text=0)
        self.observer_store.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.treeview_observers.append_column(column)


    def cleanup(self):
        print "Cleaning up"
        self.table = None  # Dereference table.
        # Close all child windows.
        for windowname in self.children.keys():
            self.children.close(windowname)


    def errback(self, failure):
        print "Error: %s" % failure.getErrorMessage()


    def setTable(self, table):
        """Changes display to match the table specified.
        
        @param table: the (now) focal table.
        """
        self.table = table
        self.table.attach(self.eventHandler)
        self.table.game.attach(self.eventHandler)
        self.player, self.position = None, None

        self.window.set_title(_('Table %s (Bridge)') % self.table.id)
        self.resetGame()

        for position in Direction:
            self.redrawHand(position)  # Redraw all hands.

        if self.table.game.inProgress():
            # If trick play in progress, redraw trick.
            if self.table.game.play:
                self.redrawTrick()
            self.setTurnIndicator()

            for call in self.table.game.bidding.calls:
                position = self.table.game.bidding.whoCalled(call)
                self.addCall(call, position)

            self.setDealer(self.table.game.board['dealer'])
            self.setVuln(self.table.game.board['vuln'])

            # If contract, set contract.
            if self.table.game.bidding.isComplete():
                contract = self.table.game.bidding.getContract()
                self.setContract(contract)

            # If playing, set trick counts.
            if self.table.game.play:
                for position, cards in self.table.game.play.played.items():
                    for card in cards:
                        self.addCard(card, position)
                self.setTrickCount(self.table.game.getTrickCount())

            # If user is a player and bidding in progress, open bidding box.
            if self.player and not self.table.game.bidding.isComplete():
                self.children.open('window_bidbox', parent=self)

        # Initialise seat menu and player labels.
        for position in Direction:
            player = self.table.players.get(position)  # Player name or None.

            available = player is None or position == self.position
            self.takeseat_items[position].set_property('sensitive', available)
            if player:
                self.event_joinGame(player, position)
            else:  # Position vacant.
                self.event_leaveGame(None, position)

        # Initialise observer listing.
        self.observer_store.clear()
        for observer in self.table.observers:
            self.event_addObserver(observer)


    def resetGame(self):
        """Clears bidding history, contract, trick counts."""
#        self.cardarea.clear()
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
        position = self.table.game.play.whoPlayed(card)
        column = position.index
        row = self.table.game.play.played[position].index(card)
        
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
        if contract['declarer'] in (Direction.North, Direction.South) and score > 0 \
        or contract['declarer'] in (Direction.East, Direction.West) and score < 0:
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
        if all is True or self.table.game.play is None:
            played = []
        else:
            played = self.table.game.play.played[position]

        try:
            hand = self.table.game.getHand(position)
            self.cardarea.set_hand(hand, position, omit=played)
        except GameError:  # Unknown hand: draw cards face down.
            cards, played = range(13), range(len(played))
            self.cardarea.set_hand(cards, position, facedown=True, omit=played)


    def redrawTrick(self):
        """Redraws trick.
        
        @param table:
        @param trick:
        """
        trick = None
        if self.table.game.play:
            trick = self.table.game.play.getCurrentTrick()
        self.cardarea.set_trick(trick)


    def setTurnIndicator(self):
        """Sets the statusbar text to indicate which player is on turn."""
        context = self.statusbar.get_context_id('turn')
        self.statusbar.pop(context)
        try:
            turn = self.table.game.getTurn()
            text = _("It is %s's turn") % str(turn)
            self.statusbar.push(context, text)
        except GameError:  # Game not in progress
            turn = None
        self.cardarea.set_turn(turn)


    def setContract(self, contract=None):
        """Sets the contract label from contract."""
        format = (contract and self.getContractFormat(contract)) or _('No contract')
        self.label_contract.set_property('sensitive', contract!=None)
        self.label_contract.set_markup('<span size="x-large">%s</span>' % format)


    def setDealer(self, dealer):
        self.label_dealer.set_markup('<b>%s</b>' % DIRECTION_SYMBOLS[dealer])


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


    def setVuln(self, vulnerable):
        self.label_vuln.set_markup('<b>%s</b>' % VULN_SYMBOLS[vulnerable])


# Registered event handlers.


    def event_addObserver(self, observer):
        self.observer_store.append([observer])


    def event_removeObserver(self, observer):

        def func(model, path, iter, user_data):
            if model.get_value(iter, 0) in user_data:
                model.remove(iter)
                return True

        self.observer_store.foreach(func, observer)


    def event_joinGame(self, player, position):
        self.cardarea.set_player_name(position, player)
        # Disable menu item corresponding to position.
        widget = self.takeseat_items[position]
        widget.set_property('sensitive', False)
        # Set player label.
        label = getattr(self, 'label_%s' % position.key.lower())
        label.set_markup('<b>%s</b>' % player)

        # If all positions occupied, disable Take Seat.
        if len(self.table.players.values()) == len(Direction):
            self.takeseat.set_property('sensitive', False)


    def event_leaveGame(self, player, position):
        self.cardarea.set_player_name(position, None)
        # Enable menu item corresponding to position.
        widget = self.takeseat_items[position]
        widget.set_property('sensitive', True)
        # Reset player label.
        label = getattr(self, 'label_%s' % position.key.lower())
        label.set_markup('<i>%s</i>' % _('Position vacant'))

        # If we are not seated, ensure Take Seat is enabled.
        if self.position is None:
            self.takeseat.set_property('sensitive', True)


    def event_start(self, board):
        #self.children.close('dialog_gameresult')
        self.resetGame()

        #self.redrawTrick()  # Clear trick.
        for position in Direction:
            self.redrawHand(position)

        self.setTurnIndicator()
        self.setDealer(board['dealer'])
        self.setVuln(board['vuln'])

        if self.player:
            d = self.player.callRemote('getHand')
            d.addCallbacks(self.table.game.revealHand, self.errback,
                           callbackKeywords={'position' : self.position})
            self.children.open('window_bidbox', parent=self)


    def event_makeCall(self, call, position):
        self.addCall(call, position)
        self.setTurnIndicator()
        if self.table.game.bidding.isComplete():
            self.children.close('window_bidbox')  # If playing.
            contract = self.table.game.bidding.getContract()
            self.setContract(contract)


    def event_playCard(self, card, position):
        # Determine the position of the hand from which card was played.
        playfrom = self.table.game.play.whoPlayed(card)
        self.addCard(card, playfrom)
        self.setTurnIndicator()
        count = self.table.game.getTrickCount()
        self.setTrickCount(count)
        self.redrawTrick()
        self.redrawHand(playfrom)


    def event_gameFinished(self):
        for position in self.table.game.deal:
            self.redrawHand(position, all=True)
        self.setTurnIndicator()

        # Determine and display score in dialog box.
        contract = self.table.game.bidding.getContract()
        if contract:
            trickCount = self.table.game.getTrickCount()
            offset = trickCount['declarerWon'] - trickCount['required']
            score = self.table.game.score()
            self.addScore(contract, trickCount['declarerWon'], score)

            textContract = _('Contract %s') % self.getContractFormat(contract)
            textTrick = (offset > 0 and _('made by %s tricks') % offset) or \
                        (offset < 0 and _('failed by %s tricks') % abs(offset)) or \
                        _('made exactly')
            scorer = (score >= 0 and _('declarer')) or _('defence')
            textScore = _('Score %s points for %s') % (abs(score), scorer)

            message = '%s %s.\n\n%s.' % (textContract, textTrick, textScore)
        else:
            message = _('Bidding passed out.')

        dialog = self.children.open('dialog_gameresult', parent=self)
        dialog.setup(message)


    def event_revealHand(self, hand, position):
        self.redrawHand(position)


    def event_messageReceived(self, message, sender, recipients):
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
        
        return _('%s%s%s by %s') % (bidlevel, bidstrain, double, declarer)


# Signal handlers.


    def on_card_clicked(self, card, position):
        if self.player:
            d = self.player.callRemote('playCard', card)
            d.addErrback(self.errback)
            #d.addErrback(lambda _: True)  # Ignore any error.


    def on_seat_activated(self, widget, position):
        
        def success(player):
            self.player = player  # RemoteReference to BridgePlayer object.
            self.position = position

            self.takeseat.set_property('sensitive', False)
            self.leaveseat.set_property('sensitive', True)
            # If game is running and bidding is active, open bidding box.
            if self.table.game.inProgress():
                d = self.player.callRemote('getHand')
                d.addCallbacks(self.table.game.revealHand, self.errback,
                               callbackKeywords={'position' : self.position})
                if not self.table.game.bidding.isComplete():
                    self.children.open('window_bidbox', parent=self)
        
        d = self.table.joinGame(position)
        d.addCallbacks(success, self.errback)


    def on_takeseat_clicked(self, widget, *args):
        # TODO: match user up with preferred partner.
        for position in Direction:
            if position not in self.table.players:  # Position is vacant.
                self.on_seat_activated(widget, position)  # Take position.
                break


    def on_leaveseat_clicked(self, widget, *args):
        
        def success(r):
            self.position = None
            self.takeseat.set_property('sensitive', True)
            self.leaveseat.set_property('sensitive', False)
            self.children.close('window_bidbox')  # If open.
        
        d = self.table.leaveGame(self.position)
        d.addCallbacks(success, self.errback)


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

