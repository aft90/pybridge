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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA


import gtk
from wrapper import GladeWrapper

import pybridge.bridge.call as Call

from config import config
from eventhandler import SimpleEventHandler
from vocabulary import *


class WindowBidbox(object):
    """The bidding box is presented to a player, during bidding.
    
    Each call (bid, pass, double or redouble) is displayed as a button.
    When it is the player's turn to bid, a call is made by clicking the
    corresponding button. Unavailable calls are shown greyed-out.
    """


    def __init__(self, parent=None):
        self.window = gtk.Window()
        if parent:
            self.window.set_transient_for(parent.window)
        self.window.set_title(_('Bidding Box'))
        self.window.connect('delete_event', self.on_delete_event)
        self.window.set_resizable(False)

        self.callButtons = {}
        self.callSelectHandler = None  # A method to invoke when a call is clicked.
        self.eventHandler = SimpleEventHandler(self)
        self.table = None
        self.position = None

        def buildButtonFromCall(call, markup):
            button = gtk.Button()
            button.set_relief(gtk.RELIEF_NONE)
            button.connect('clicked', self.on_call_clicked, call)
            # A separate label is required for marked-up text.
            label = gtk.Label()
            label.set_markup(markup)
            label.set_use_markup(True)
            button.add(label)
            self.callButtons[call] = button
            return button

        vbox = gtk.VBox()

        bidtable = gtk.Table(rows=7, columns=5, homogeneous=True)
        vbox.pack_start(bidtable)
        # Build buttons for all bids.
        for y, level in enumerate(Call.Level):
            for x, strain in enumerate(Call.Strain):
                bid = Call.Bid(level, strain)
                markup = render_call(bid)
                xy = (x, x+1, y, y+1)
                bidtable.attach(buildButtonFromCall(bid, markup), *xy)

        vbox.pack_start(gtk.HSeparator())

        otherbox = gtk.HBox()
        vbox.pack_start(otherbox)
        # Build buttons for other calls.
        othercalls = [(Call.Pass(), render_call_name, True),
                      (Call.Double(), render_call, False),
                      (Call.Redouble(), render_call, False)]
        for call, renderer, expand in othercalls:
            markup = renderer(call)
            otherbox.pack_start(buildButtonFromCall(call, markup), expand)

        self.window.add(vbox)
        self.window.show_all()


    def tearDown(self):
        if self.table:
            self.table.game.detach(self.eventHandler)
        self.table = None  # Dereference table.


    def setCallSelectHandler(self, handler):
        """Provide a method to invoke when user selects a call.
        
        @param handler: a method accepting a call argument.
        @type handler: function
        """
        self.callSelectHandler = handler


    def setTable(self, table, position):
        """Monitor the state of bidding in game at specified table.
        
        @param table: the BridgeGame for which to observe bidding session.
        @param: 
        """
        if self.table:
            self.table.game.detach(self.eventHandler)

        self.table = table
        self.table.game.attach(self.eventHandler)
        self.position = position

        self.enableCalls()


# Event handlers.


    def event_makeCall(self, call, position):
        self.enableCalls()


# Utility methods.


    def enableCalls(self):
        """Enables buttons representing the calls available to player."""
        if self.position == self.table.game.getTurn():
            self.window.set_property('sensitive', True)
            for call, button in self.callButtons.items():
                isvalid = self.table.game.bidding.isValidCall(call)
                button.set_property('sensitive', isvalid)
        else:
            self.window.set_property('sensitive', False)


# Signal handlers.


    def on_call_clicked(self, widget, call):
        if self.callSelectHandler:
            self.callSelectHandler(call)  # Invoke external handler.


    def on_delete_event(self, widget, *args):
        return True  # Stops window deletion taking place.

