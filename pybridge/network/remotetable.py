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


from twisted.spread import pb
from zope.interface import implements

from pybridge.interfaces.observer import ISubject
from pybridge.interfaces.table import ITable
from pybridge.network.error import DeniedRequest, IllegalRequest

from pybridge.games import SUPPORTED_GAMES


class RemoteTable(pb.RemoteCache):
    """A client-side implementation of ITable providing a "front-end" to a
    remote server-side LocalTable.
    
    RemoteTable mirrors the state of LocalTable as a local cache. External code
    may, therefore, read the table state without network communication. Actions
    which change the table state are forwarded to the LocalTable.
    """

    implements(ITable, ISubject)

    info = property(lambda self: {'gamename': self.game.__class__.__name__})


    def __init__(self):
        self.listeners = []


    def setCopyableState(self, state):
        self.id = state['id']
        if state['gamename'] in SUPPORTED_GAMES:
            gameclass = SUPPORTED_GAMES[state['gamename']]
            self.game = gameclass()
            self.game.setState(state['gamestate'])
        else:
            raise NameError, "Unsupported game class %s" % state['gamename']

        self.chat = state['chat']
        self.observers = state['observers']
        self.players = state['players']
        for position in self.players:
            self.game.addPlayer(position)
        self.__view = state['view']


# Implementation of ITable.


    def joinGame(self, position, user=None):
        d = self.__view.callRemote('joinGame', position)
        return d


    def leaveGame(self, position, user=None):
        d = self.__view.callRemote('leaveGame', position)
        return d


# Implementation of ISubject.


    def attach(self, listener):
        self.listeners.append(listener)


    def detach(self, listener):
        self.listeners.remove(listener)


    def notify(self, event, *args, **kwargs):
        for listener in self.listeners:
            listener.update(event, *args, **kwargs)


# Remote update methods.


    def observe_addObserver(self, observer):
        self.observers.append(observer)
        self.notify('addObserver', observer)


    def observe_removeObserver(self, observer):
        self.observers.remove(observer)
        self.notify('removeObserver', observer)


    def observe_joinGame(self, player, position):
        self.game.addPlayer(position)
        self.players[position] = player
        self.notify('joinGame', player, position)


    def observe_leaveGame(self, player, position):
        self.game.removePlayer(position)
        del self.players[position]
        self.notify('leaveGame', player, position)


    def observe_sendMessage(self, message, sender, recipients):
        # TODO: add to message log?
        self.notify('sendMessage', message, sender, recipients)


    def observe_gameUpdate(self, event, *args, **kwargs):
        self.game.updateState(event, *args, **kwargs)

