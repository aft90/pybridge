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


from zope.interface import implements

from pybridge.interfaces.table import ITableEvents
from pybridge.interfaces.bridgetable import IBridgeTableEvents
from pybridge.interfaces.serverstate import IServerEvents



class EventHandler:
    """An implementation of ITableEvents."""

    implements(IServerEvents, ITableEvents, IBridgeTableEvents)


    def __init__(self):
        self.callbacks = {}


# Implementation of IServerEvents.


    def connectionLost(self, connector, reason):
        print "lost connection -", reason.getErrorMessage()
        self.runCallbacks('connectionLost', connector, reason)


    def tableOpened(self, table):
        self.runCallbacks('tableOpened', table)


    def tableClosed(self, table):
        self.runCallbacks('tableClosed', table)


    def userLoggedIn(self, user):
        self.runCallbacks('userLoggedIn', user)


    def userLoggedOut(self, user):
        self.runCallbacks('userLoggedOut', user)


# Implementation of ITableEvents.


    def observerAdded(self, table, observer):
        self.runCallbacks('observerAdded', table, observer)


    def observerRemoved(self, table, observer):
        self.runCallbacks('observerRemoved', table, observer)


    def playerAdded(self, table, player, position):
        self.runCallbacks('playerAdded', table, player, position)


    def playerRemoved(self, table, player, position):
        self.runCallbacks('playerRemoved', table, player, position)


    def messageReceived(self, table, message, sender, recipients):
        print "%s says: %s" % (sender, message) 
        self.runCallbacks('messageReceived', table, message, sender, recipients)


# Implementation of IBridgeTableEvents.


    def gameStarted(self, table, dealer, vulnNS, vulnEW):
        self.runCallbacks('gameStarted', table, dealer, vulnNS, vulnEW)


    def gameFinished(self, table):
        self.runCallbacks('gameFinished', table)


    def gameCallMade(self, table, call, position):
        self.runCallbacks('gameCallMade', table, call, position)


    def gameCardPlayed(self, table, card, position):
        self.runCallbacks('gameCardPlayed', table, card, position)


    def gameHandRevealed(self, table, hand, position):
        self.runCallbacks('gameHandRevealed', table, hand, position)


# Methods to manipulate the callback lists.


    def registerCallback(self, event, callback):
        """Places callback onto notification list for event."""
        if not self.callbacks.get(event):
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
        return True


    def unregisterCallback(self, event, callback):
        """Removes callback from notification list for event."""
        if callback in self.callbacks.get(event, []):
            self.callbacks[event].remove(callback)
            return True
        return False


    def runCallbacks(self, event, *args, **kwargs):
        for callback in self.callbacks.get(event, []):
            callback(*args, **kwargs)


eventhandler = EventHandler()

