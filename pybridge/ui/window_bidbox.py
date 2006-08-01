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
from wrapper import GladeWrapper

from eventhandler import eventhandler

from pybridge.bridge.call import Bid, Pass, Double, Redouble
from pybridge.bridge.call import Level, Strain

CALL_NAMES = {'bid' : Bid, 'pass' : Pass,
              'double' : Double, 'redouble' : Redouble, }

LEVEL_NAMES = {'1' : Level.One, '2' : Level.Two, '3' : Level.Three,
               '4' : Level.Four, '5' : Level.Five, '6' : Level.Six,
               '7' : Level.Seven, }

STRAIN_NAMES = {'club' : Strain.Club, 'diamond' : Strain.Diamond,
                'heart' : Strain.Heart, 'spade' : Strain.Spade,
                'nt' : Strain.NoTrump, }

ALL_CALLS = [Pass(), Double(), Redouble()] + \
            [Bid(l, s) for l, s in zip(list(Level)*5, list(Strain)*7)]


class WindowBidbox(GladeWrapper):
    """The bidding box is presented to a player, during bidding.
    
    Each call (bid, pass, double or redouble) is displayed as a button.
    When it is the player's turn to bid, a call is made by clicking the
    corresponding button. Unavailable calls are shown greyed-out.
    """

    glade_name = 'window_bidbox'


    def new(self):
        table = self.parent.focalTable
        self.set_available_calls(table.seated, table.game.bidding)
        
        eventhandler.registerCallback('gameCallMade', self.gameCallMade)


    def gameCallMade(self, table, call, position):
        if table == self.parent.focalTable:
            self.set_available_calls(table.seated, table.game.bidding)

            # If bidding is complete, close this window.
            if table.game.bidding.isComplete():
                self.window.destroy()


    def set_available_calls(self, seat, bidding):
        """Enables buttons representing the given calls."""
        if bidding.whoseTurn() == seat:
            self.window.set_property('sensitive', True)
            for call in ALL_CALLS:
                button = self.get_button_from_call(call)
                button.set_property('sensitive', bidding.isValidCall(call))
        else:
            self.window.set_property('sensitive', False)


    def on_call_clicked(self, widget, *args):
        """Builds a call object and submits."""
        # Do not check validity of call: the server will do that.
        # If call is invalid, ignore the resultant errback.
        call = self.get_call_from_button(widget)
        d = self.parent.focalTable.gameMakeCall(call)
        d.addErrback(lambda r: True)  # Ignore error.


    def get_button_from_call(self, call):
        """Returns a pointer to GtkButton object representing given call."""
        callname = [k for k,v in CALL_NAMES.items() if isinstance(call, v)][0]
        if isinstance(call, Bid):
            level = [k for k,v in LEVEL_NAMES.items() if v==call.level][0]
            strain = [k for k,v in STRAIN_NAMES.items() if v==call.strain][0]
            return getattr(self, 'button_%s_%s_%s' % (callname, level, strain))
        else:
            return getattr(self, 'button_%s' % callname)


    def get_call_from_button(self, widget):
        """Returns an instance of the call represented by given GtkButton."""
        text = widget.get_name().split('_')  # "button", calltype, level, strain
        calltype = CALL_NAMES[text[1]]
        if calltype == Bid:
            level = LEVEL_NAMES[text[2]]
            strain = STRAIN_NAMES[text[3]]
            return calltype(level, strain)
        return calltype()


    def on_window_bidbox_delete_event(self, widget, *args):
        return True  # Stops window deletion taking place.

