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


import time
from twisted.internet import reactor
from twisted.spread import pb
from zope.interface import implements

from pybridge.interfaces.observer import ISubject, IListener
from pybridge.interfaces.table import ITable
from pybridge.network.error import DeniedRequest, IllegalRequest


class LocalTable(pb.Cacheable):
    """An implementation of ITable suitable for server-side table instances.
    
    A LocalTable maintains the "master" game object and provides synchronisation
    services for remote tables to mirror the game state.
    """

    implements(ITable, ISubject, IListener)

    info = property(lambda self: {'game': self.gametype.__name__})


    def __init__(self, id, gametype, config={}):
        self.listeners = []

        self.id = id
        self.gametype = gametype
        self.game = gametype()  # Initialise game.
        self.game.attach(self)  # Listen for game events.

        self.observers = {}  # For each user perspective, a remote ITableEvents.
        self.players = {}  # Positions mapped to perspectives of game players.
        self.view = LocalTableViewable(self)  # For remote clients.

        # Configuration variables.
        self.config = {}
        self.config['CloseWhenEmpty'] = True
        self.config['MultiplePlayersPerUser'] = False
        self.config['TimeCreated'] = tuple(time.localtime())
        self.config.update(config)


    def getStateToCacheAndObserveFor(self, perspective, observer):
        # Inform existing observers that a new user has joined.
        self.notify('addObserver', observer=perspective.name)
        self.observers[perspective] = observer

        # Build a dict of public information about the table.
        state = {}
        state['id'] = self.id
        state['gametype'] = self.gametype.__name__
        state['gamestate'] = self.game.getState()
        state['observers'] = [p.name for p in self.observers.keys()]
        state['players'] = dict([(pos, p.name)
                                 for pos, p in self.players.items()])

        return state  # To observer.


    def stoppedObserving(self, perspective, observer):
        del self.observers[perspective]

        # If user was playing, then remove their player(s) from game.
        for position, user in self.players.items():
            if perspective == user:
                self.leaveGame(perspective, position)
        self.notify('removeObserver', observer=perspective.name)

        # If there are no remaining observers, close table.
        if self.config.get('CloseWhenEmpty') and not self.observers:
            self.server.tables.closeTable(self)


# Implementation of ISubject.


    def attach(self, listener):
        self.listeners.append(listener)


    def detach(self, listener):
        self.listeners.remove(listener)


    def notify(self, event, *args, **kwargs):
        for listener in self.listeners:
            listener.update(event, *args, **kwargs)
        # For all observers, calls event handler with provided arguments.
        for observer in self.observers.values():
            self.notifyObserver(observer, event, *args, **kwargs)


    def notifyObserver(self, obs, event, *args, **kwargs):
        """Calls observer's event handler with provided arguments.
        
        @param obs: an observer object.
        @type obs: RemoteCacheObserver
        @param event: the name of the event.
        @type event: str
        """
        # Event handlers are called on the next iteration of the reactor,
        # to allow the caller of this method to return a result.
        reactor.callLater(0, obs.callRemote, event, *args, **kwargs)


# Implementation of IListener.


    def update(self, event, *args, **kwargs):
        # Expected to be called only by methods of self.game.
        for observer in self.observers.values():
            self.notifyObserver(observer, 'gameUpdate', event, *args, **kwargs)


# Implementation of ITable.


    def joinGame(self, user, position):
        if position not in self.game.positions:
            raise IllegalRequest, "Invalid position type"
        # Check that user is not already playing at table.
        if not self.config.get('MultiplePlayersPerUser'):
            if user in self.players.values():
                raise DeniedRequest, "Already playing in game"

        player = self.game.addPlayer(position)  # May raise GameError.
        self.players[position] = user
        self.notify('joinGame', player=user.name, position=position)

        return player


    def leaveGame(self, user, position):
        if position not in self.game.positions:
            raise IllegalRequest, "Invalid position type"
        # Ensure that user is playing at specified position.
        if self.players.get(position) != user:
            raise DeniedRequest, "Not playing at position"

        self.game.removePlayer(position)  # May raise GameError.
        del self.players[position]
        self.notify('leaveGame', player=user.name, position=position)


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
            self.notifyObserver(observer, 'sendMessage', message=message,
                                sender=sender.name, recipients=recipients)




class LocalTableViewable(pb.Viewable):
    """Provides a public front-end to an instantiated LocalTable.
    
    Serialization flavors are mutually exclusive and cannot be mixed,
    so this class is a subclass of pb.Viewable.
    """


    def __init__(self, table):
        """
        
        @param table: a instantiated LocalTable.
        """
        self.table = table


    def view_joinGame(self, user, position):
        # TODO: return a deferred?
        return self.table.joinGame(user, position)


    def view_leaveGame(self, user, position):
        return self.table.leaveGame(user, position)


    def view_sendMessage(self, user, message, sender=None, recipients=[]):
        return self.table.sendMessage(message, sender=user,
                                      recipients=recipients)

