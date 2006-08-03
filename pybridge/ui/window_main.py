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

TABLE_ICON = environment.find_pixmap("table.png")


class WindowMain(GladeWrapper):

    glade_name = 'window_main'


    def new(self):
        self.tables = {}   # For each observed table, a dict of UI data.
        self.table = None  # Table currently displayed in window.
        
        # Set up table model and icon view.
        self.tableview_icon = gtk.gdk.pixbuf_new_from_file(TABLE_ICON)        
        self.tableview.set_text_column(0)
        self.tableview.set_pixbuf_column(1)
        self.tableview_model = gtk.ListStore(str, gtk.gdk.Pixbuf)
        self.tableview.set_model(self.tableview_model)
        
        # Register events.
        eventhandler.registerCallback('tableOpened', self.event_tableOpened)
        eventhandler.registerCallback('tableClosed', self.event_tableClosed)
        eventhandler.registerCallback('gameStarted', self.event_gameStarted)
        eventhandler.registerCallback('gameFinished', self.event_gameFinished)
        eventhandler.registerCallback('gameCardPlayed', self.event_gameCardPlayed)
        eventhandler.registerCallback('gameHandRevealed', self.event_gameHandRevealed)


    def joinedTable(self, table):
        """Actions to perform when user has joined a table."""
        self.tables[table] = {}
        
        # Set up cardarea widget.
        cardarea = CardArea()
        cardarea.on_card_clicked = lambda c, p: table.gamePlayCard(c, p)
        cardarea.show()
        self.tables[table]['cardarea'] = cardarea
        
        # Set up new page, with cardarea and tab.
        tab = gtk.Label(table.id)
        index = self.notebook.append_page(cardarea, tab)
        self.tables[table]['tabindex'] = index
        self.notebook.set_current_page(index)


    def leftTable(self, table):
        """Actions to perform when user has left a table."""
        
        # Remove table page.
        self.notebook.remove_page(self.tables[table]['tabindex'])
        del self.tables[table]
        
        # Check for any remaining tables.
        if len(self.tables) == 0:
            utils.windows.close('window_game')


    def switchTable(self, table):
        """"""
        self.table = table

        if table and table.game:
            # Redraw hands and, if playing in progress, redraw trick.
            for position in table.game.deal:
                self.redrawHand(table, position)
            if table.game.playing:
                self.redrawTrick(table)
        
        window = utils.windows.get('window_game')
        if table:
            if window is None:  # Launch window.
                window = utils.windows.open('window_game', self)
            window.changeTable(table)
        else:
            if window:
                utils.windows.close('window_game')
 

    def redrawHand(self, table, position, all=False):
        """Redraws cards making up the hand at position.
        
        Cards played are filtered out and omitted from display.
        Unknown cards are displayed face down.
        
        @param table:
        @param position:
        @param all: If True, do not filter out cards played.
        """
        hand = table.game.deal[position]
        played = []
        if table.game.playing:
            played = table.game.playing.played[position]
        
        if hand and all is True:  # Own or known hand: show all cards.
            cards = hand
        elif hand:  # Own or known hand: filter out cards played.
            cards = [((card not in played and card) or None) for card in hand]
        else:  # Unknown hand: show cards face down.
            cards = ['FACEDOWN']*(13-len(played)) + [None]*len(played)
        
        # dummy = self.game.playing != None and seat == self.game.playing.dummy
        # transpose = dummy and seat in (Seat.North, Seat.South)
        cardarea = self.tables[table]['cardarea']
        cardarea.build_hand(position, cards)
        cardarea.draw_hand(position)


    def redrawTrick(self, table, trick=None):
        """Redraws trick.
        
        @param table:
        @param trick:
        """
        # TODO: this cannot be called until playing in progress
        # perhaps put a clear() method in cardarea?
        if trick is None:
            trick = table.game.playing.getCurrentTrick()
        
        cardarea = self.tables[table]['cardarea']
        cardarea.build_trick(trick)
        cardarea.draw_trick()


    def setTurnIndicator(self, turn=None):
        """Sets the statusbar text to indicate which player is on turn."""
        context = self.statusbar.get_context_id('turn')
        self.statusbar.pop(context)
        if turn is not None:
            self.statusbar.push(context, "It is %s's turn" % str(turn))


#    def getActiveTable(self):
#        """Returns table currently displayed to user, or None."""
#        active = self.notebook.get_current_page()
#        for table in self.tables:
#            if self.tables[table]['tabindex'] == active:
#                return table
#        return None


# Registered event handlers.


    def event_tableOpened(self, tableid):
        """Adds a table to the table listing."""
        self.tableview_model.append([tableid, self.tableview_icon])


    def event_tableClosed(self, tableid):
        """Removes a table from the table listing."""
        
        def func(model, path, iter, user_data):
            if model.get_value(iter, 0) in user_data:
                model.remove(iter)
            return True
        
        self.tableview_model.foreach(func, tableid)


    def event_gameStarted(self, table, dealer, vulnNS, vulnEW):
        if table == self.table:
            for position in table.game.deal:
                self.redrawHand(table, position)
        # TODO: Clear trick.
#       self.switchTable(table)


    def event_gameFinished(self, table):
        if table == self.table:
            for position in table.game.deal:
                self.redrawHand(table, position, all=True)


    def event_gameCardPlayed(self, table, card, position):
        if table == self.table:
            self.redrawHand(table, position)
            self.redrawTrick(table)


    def event_gameHandRevealed(self, table, hand, position):
        if table == self.table:
            self.redrawHand(table, position)


# Signal handlers.


    def on_notebook_switch_page(self, notebook, page, page_num):
        table = None
        for table in self.tables:
            if self.tables[table]['tabindex'] == page_num:
                break
        self.table = table
        self.switchTable(table)


    def on_tableview_item_activated(self, iconview, path, *args):
        iter = self.tableview_model.get_iter(path)
        tableid = self.tableview_model.get_value(iter, 0)
        if tableid not in client.tables:
            d = client.joinTable(tableid)
            d.addCallback(self.joinedTable)


    def on_window_main_delete_event(self, widget, *args):
        utils.quit()


    def on_newtable_activate(self, widget, *args):
        utils.windows.open('dialog_newtable', self)


    def on_jointable_activate(self, widget, *args):
        print self.tableview.get_cursor()


    def on_disconnect_activate(self, widget, *args):
        client.disconnect()
        utils.windows.close('window_main')
        utils.windows.open('dialog_connection')


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

