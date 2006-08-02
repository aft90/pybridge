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


import time
from twisted.internet import reactor
from twisted.spread import pb
from zope.interface import implements

from pybridge.interfaces.table import ITable
from pybridge.network.error import DeniedRequest, IllegalRequest

from pybridge.bridge.deck import Seat  # XX TODO: Try to avoid this.


class LocalTable(pb.Cacheable):
    """"""

    implements(ITable)


    def __init__(self, id):
        self.id = id
        self.config = {}
        self.observers = {}  # For each perspective, a remote ITableEvents observer.
        self.players = {}    # For each position, the player's perspective.
        
        # Configuration variables.
        self.config['closeWhenEmpty'] = True
        self.config['timeCreated'] = time.localtime()


    def getStateToCacheAndObserveFor(self, perspective, observer):
        self.updateObservers('observerAdded', observer=perspective.name)
        self.observers[perspective] = observer
        
        return self.getState()  # For observer.
        

    def getState(self):
        """Build a dict of public information about the table."""
        state = {}
        
        state['id'] = self.id
        state['observers'] = [p.name for p in self.observers.keys()]
        state['players'] = {}
        for position, perspective in self.players.items():
            state['players'][position.key] = getattr(perspective, 'name', None)
#        state['timeCreated'] = self.config['timeCreated']
        
        return state


    def stoppedObserving(self, perspective, observer):
        del self.observers[perspective]
        
        # If user was a player, then remove player.
        if self.getPositionOfPlayer(perspective):
            self.removePlayer(perspective)
        
        self.updateObservers('observerRemoved', observer=perspective.name)
        
        # If there are no remaining observers, close table.
        if self.config.get('closeWhenEmpty') and len(self.observers) == 0:
            self.server.tables.closeTable(self)


# Methods implementing ITable.


    def addPlayer(self, position, player):
        # Check that player is not already playing at table.
        if self.getPositionOfPlayer(player):
            raise DeniedRequest('already playing at table')
        # Check that position is not occupied by another player.
        if self.players.get(position) is not None:
            raise DeniedRequest('position occupied by another player')
        
        self.players[position] = player
        self.updateObservers('playerAdded', player=player.name, position=position.key)


    def removePlayer(self, player):
        position = self.getPositionOfPlayer(player)
        # Check that player is playing at table:
        if not position:
            raise DeniedRequest('not playing at table')
        
        self.players[position] = None
        self.updateObservers('playerRemoved', player=player.name, position=position.key)


    def sendMessage(self, message, sender, recipients):
        names = [perspective.name for perspective in self.observers.keys()]
        if recipients:  # Translate user names to their observer objects.
            # Remove user names without a perspective object observing table.
            recipients = [name for name in recipients if name in names]
            sendTo = [o for p, o in self.observers.items() if p.name in recipients]
        else:  # Broadcast message to all observers.
            recipients = names
            sendTo = self.observers.values()
        
        for observer in sendTo:
            observer.callRemote('messageReceived', message, sender.name, recipients)


# Utility methods.


    def getPositionOfPlayer(self, user):
        """If observer is playing, returns position of player.
        Otherwise, returns False.
        
        @param user: observer identifier.
        @return: position of player, or False.
        """
        for position, player in self.players.items():
            if player == user:
                return position
        return False


    def informObserver(self, obs, event, *args, **kwargs):
        """Calls observer's event handler with provided args and kwargs.
        
        Event handlers are called on the next iteration of the reactor,
        to allow the caller of this method to return a result.
        """
        reactor.callLater(0, obs.callRemote, event, *args, **kwargs)


    def updateObservers(self, event, *args, **kwargs):
        """For each observer, calls event handler with provided kwargs."""
        for observer in self.observers.values():
            self.informObserver(observer, event, *args, **kwargs)




class LocalTableViewable(pb.Viewable):
    """
    
    Serialization flavors are mutually exclusive and cannot be mixed,
    so this class provides a pb.Viewable front-end to LocalTable.
    """


    def __init__(self, table):
        """
        
        @param table: a instantiated LocalTable.
        """
        self.table = table


    def view_addPlayer(self, user, position, player=None):
        position = getattr(Seat, position)  # XX
        self.table.addPlayer(position, user)


    def view_removePlayer(self, user, player=None):
        self.table.removePlayer(user)


    def view_sendMessage(self, user, message, sender=None, recipients=[]):
        self.table.sendMessage(message, user, recipients)

