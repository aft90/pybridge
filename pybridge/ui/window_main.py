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

from pybridge.conf import PYBRIDGE_VERSION
from pybridge.environment import environment
from pybridge.network.client import client

from cardarea import CardArea
from eventhandler import eventhandler
import utils


class WindowMain(GladeWrapper):

    glade_name = 'window_main'


    def new(self):
        self.tabletabs = {}  # For each observed table, its tab index.
        
        # Set up table listing.
        self.tablelisting_store = gtk.ListStore(str)
        self.tablelisting.set_model(self.tablelisting_store)
        cell_renderer = gtk.CellRendererText()
        for index, title in enumerate( ('Name',) ):
            column = gtk.TreeViewColumn(title, cell_renderer, text=index)
            self.tablelisting.append_column(column)
        
        self.focalTable = None  # Table currently being viewed.
        
        # Register events.
        eventhandler.registerCallback('tableOpened', self.eventTableOpened)
        eventhandler.registerCallback('tableClosed', self.removeTables)
        eventhandler.registerCallback('playerAdded', self.eventPlayerAdded)
        eventhandler.registerCallback('gameStarted', self.gameStarted)
        eventhandler.registerCallback('gameFinished', self.gameFinished)
        eventhandler.registerCallback('gameCardPlayed', self.gameCardPlayed)
        eventhandler.registerCallback('gameHandRevealed', self.gameHandRevealed)


# Registered event handlers.


    def eventTableOpened(self, tableid):
        """Adds a table to the table listing."""
        row = (tableid, )
        iter = self.tablelisting_store.append(row)


    def removeTables(self, *tableids):
        """Removes a table from the table listing."""
        
        def func(model, path, iter, user_data):
            if model.get_value(iter, 0) in user_data:
                model.remove(iter)
            return True
        
        self.tablelisting_store.foreach(func, tableids)


    def joinedTable(self, table):
        """Actions to perform when user has joined a table."""
        # Set up card area widget as new page.
        tab = gtk.Label(table.id)
        self.cardarea = CardArea()
        self.cardarea.on_card_clicked = self.on_card_clicked
        self.cardarea.show()
        
        index = self.notebook.append_page(self.cardarea, tab)
        self.tabletabs[table] = index

        self.changeTable(table)


    def eventPlayerAdded(self, table, player, position):
        """"""
        if table == self.focalTable and player == client.username:
            if table.game and not table.game.bidding.isComplete():
                utils.openWindow('window_bidbox', self)


    def changeTable(self, table):
        """Call when focus changes to a table.
        
        Changes display to match the table specified.
        """
        # Switch focus to table.
        self.focalTable = table
        self.notebook.set_current_page(self.tabletabs[table])
        
        if table.game:
            # If user is a player and bidding in progress, launch bidding box.
            if table.getPositionOfPlayer(client.username) and not table.game.bidding.isComplete():
                if not utils.getWindow('window_bidbox'):
                    utils.openWindow('window_bidbox', self)
            # Otherwise, if bidding box is open, close it down.
            elif utils.getWindow('window_bidbox'):
                utils.closeWindow('window_bidbox')
            
            for position in table.game.deal:
                self.redrawHand(position)
            if table.game.playing:
                self.redrawTrick()
        
        if not utils.getWindow('window_game'):  # Display game window.
            utils.openWindow('window_game', self)
        utils.getWindow('window_game').changeTable(table)


    def leftTable(self, table):
        """Actions to perform when user has left a table."""
        # Switch focus away from table.
        self.notebook.remove_page(self.notebook.get_n_pages() - 1)  # TODO: fix this.
        self.focalTable = None  # TODO: fix this also.
        utils.closeWindow('window_game')  # & bidbox?


    def set_turn(self, turn=None):
        """Sets the statusbar text to indicate which player is on turn."""
        context = self.statusbar.get_context_id('turn')
        self.statusbar.pop(context)
        if turn is not None:
            self.statusbar.push(context, "It is %s's turn" % str(turn))


# Game events.


    def gameStarted(self, table, dealer, vulnNS, vulnEW):
        if table == self.focalTable:
            self.changeTable(table)
#            
##            self.chanseated = table.getPositionOfPlayer(client.username)
#            
#            # Draw hidden hands (gameHandRevealed draws visible hands)
#            for position in table.game.deal.keys():
#                if not table.game.isHandVisible(position, seated):
#                    cards = ['facedown']*13  # TODO: what about other games?
#                    self.cardarea.build_hand(position, cards)
#                    self.cardarea.draw_hand(position)
#            
#            if table.seated:  # If playing, launch bidding box.
#                utils.openWindow('window_bidbox', self)


    def gameFinished(self, table):
        if self.focalTable.game.playing and self.focalTable.game.playing.isComplete():
            # Display cards in order played.
            for seat, cards in self.focalTable.game.playing.played.items():
                self.cardarea.build_hand(seat, cards)
                self.cardarea.draw_hand(seat)
        else:
            # Display cards from all hands.
            pass

        if self.focalTable.game.isComplete():
            # Determine and display score.
            pass


    def gameCardPlayed(self, table, card, position):
        if table == self.focalTable:
            self.redrawHand(position)
            self.redrawTrick()


    def gameHandRevealed(self, table, hand, position):
        if table == self.focalTable:
            self.redrawHand(position)


    def redrawHand(self, position, all=False):
        """Redraws cards making up the hand at position.
        
        Cards played are filtered out and omitted from display.
        Unknown cards are displayed face down.

        @param position:
        @param all: If True, do not filter out cards played.
        """
        hand = self.focalTable.game.deal[position]
        if self.focalTable.game.playing:
            played = self.focalTable.game.playing.played[position]
        else:
            played = []

        if hand and all is True:  # Own or known hand: show all cards.
            cards = hand
        elif hand:  # Own or known hand: filter out cards played.
            cards = [((card not in played and card) or None) for card in hand]
        else:  # Unknown hand: show cards face down.
            cards = ['FACEDOWN']*(13-len(played)) + [None]*len(played)
        
        # dummy = self.game.playing != None and seat == self.game.playing.dummy
        # transpose = dummy and seat in (Seat.North, Seat.South)
        self.cardarea.build_hand(position, cards)
        self.cardarea.draw_hand(position)


    def redrawTrick(self, leader=None, trick=None):
        """Redraws trick.

        @param leader: position of player to play first card in trick.
        @param trick: dict of cards played, keyed by player position.
        """
        if leader is None or trick is None:
            index = self.focalTable.game.playing.currentTrick()
            leader, trick = self.focalTable.game.playing.getTrick(index)
        
        self.cardarea.build_trick((leader, trick))
        self.cardarea.draw_trick()
        

# Signal handlers.


    def on_card_clicked(self, card, position):
        # Do not check validity of card play: the server will do that.
        # If card play is invalid, ignore the resultant errback.
        d = self.focalTable.gamePlayCard(card, position)
        d.addErrback(lambda r: True)  # Ignore error.


    def on_tablelisting_row_activated(self, widget, *args):
        iter = self.tablelisting_store.get_iter(args[0])
        tableid = self.tablelisting_store.get_value(iter, 0)
        if tableid not in client.tables:
            d = client.joinTable(tableid)
            d.addCallback(self.joinedTable)


    def on_window_main_delete_event(self, widget, *args):
        utils.quit()


    def on_newtable_activate(self, widget, *args):
        utils.openWindow('dialog_newtable', self)


    def on_jointable_activate(self, widget, *args):
        print self.tablelisting.get_cursor()


    def on_disconnect_activate(self, widget, *args):
        client.disconnect()
        utils.closeWindow('window_main')
        utils.openWindow('dialog_connection')


    def on_fullscreen_activate(self, widget, *args):
        if self.menu_fullscreen.active:
            self.window.fullscreen()
        else:
            self.window.unfullscreen()


    def on_quit_activate(self, widget, *args):
        utils.quit()


    def on_about_activate(self, widget, *args):
        about = gtk.AboutDialog()
        about.set_name('PyBridge')
        about.set_version(PYBRIDGE_VERSION)
        about.set_copyright('Copyright (C) 2004-2006 Michael Banks')
        about.set_comments('A free online bridge game.')
        about.set_website('http://pybridge.sourceforge.net/')
        license = file(environment.find_doc('COPYING')).read()
        about.set_license(license)
        authorsfile = file(environment.find_doc('AUTHORS'))
        authors = [author.strip() for author in authorsfile.readlines()]
        about.set_authors(authors)
        logo_path = environment.find_pixmap('pybridge.png')
        logo = gtk.gdk.pixbuf_new_from_file(logo_path)
        about.set_logo(logo)
        
        about.run()
        about.destroy()
