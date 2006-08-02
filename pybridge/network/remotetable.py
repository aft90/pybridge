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


from twisted.spread import pb
from zope.interface import implements

from pybridge.interfaces.table import ITable
from pybridge.network.error import DeniedRequest, IllegalRequest

from pybridge.bridge.deck import Seat  # XX TODO: Try to avoid this.


class RemoteTable(pb.RemoteCache):
    """
    
    """

    implements(ITable)


    def __init__(self):
        self.master = None  # Server-side ITable object.
        self.eventHandler = None  # Expected to be set.
        
        self.id = None
        self.observers = []
        self.players = {}
        self.seated = None  # If user is playing at table.


    def setCopyableState(self, state):
        self.id = state['id']
        self.observers = state['observers']
        self.players = state['players']


    def setEventHandler(self, handler):
        self.eventHandler = handler


# Methods implementing ITable.


    def addPlayer(self, position, player=None):
        d = self.master.callRemote('addPlayer', position.key)
        d.addCallback(lambda _: setattr(self, 'seated', position))
        return d


    def removePlayer(self, player=None):
        d = self.master.callRemote('removePlayer')
        d.addCallback(lambda _: setattr(self, 'seated', None))
        return d


    def sendMessage(self, message, sender=None, recipients=[]):
        d = self.master.callRemote('sendMessage', message, recipients)
        return d


# Remote update methods.


    def observe_observerAdded(self, observer):
        self.observers.append(observer)
        self.eventHandler.observerAdded(self, observer)


    def observe_observerRemoved(self, observer):
        self.observers.remove(observer)
        self.eventHandler.observerRemoved(self, observer)


    def observe_playerAdded(self, player, position):
        position = getattr(Seat, position)  # XX
        self.players[position] = player
        self.eventHandler.playerAdded(self, player, position)


    def observe_playerRemoved(self, player, position):
        position = getattr(Seat, position)  # XX
        self.players[position] = None
        self.eventHandler.playerRemoved(self, player, position)


    def observe_messageReceived(self, message, sender, recipients):
        self.eventHandler.messageReceived(self, message, sender, recipients)


# Utility methods.


    def getPositionOfPlayer(self, user=None):
        """If user is playing, returns position of player, otherwise False.
        
        @param user: observer identifier. 
        @return: position of player, or False.
        """
        for position, player in self.players.items():
            if player == user:
                return position
        return False

