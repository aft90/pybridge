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


from UserDict import IterableUserDict
from twisted.internet import reactor
from twisted.spread import pb
from zope.interface import implements

from pybridge.interfaces.observer import ISubject


class Roster(IterableUserDict):
    """A dictionary-like object, which combines a set of available items with
    information associated with each item.
    
    This class implements the ISubject interface to provide notifications
    when an entry in the roster is added, removed or changed.
    """

    implements(ISubject)


    def __init__(self):
        IterableUserDict.__init__(self)
        self.listeners = []


    def attach(self, listener):
        self.listeners.append(listener)


    def detach(self, listener):
        self.listeners.remove(listener)


    def notify(self, event, *args, **kwargs):
        for listener in self.listeners:
            listener.update(event, *args, **kwargs)




class LocalRoster(Roster, pb.Cacheable):
    """A server-side 'master copy' of a Roster.
    
    Changes to the LocalRoster are relayed to registered RemoteRoster objects
    as well as to all local listeners.
    """


    def __init__(self):
        Roster.__init__(self)
        self.observers = []


    def getStateToCacheAndObserveFor(self, perspective, observer):
        self.observers.append(observer)
        # Assumes that each item has an 'info' attribute.
        return dict([(id, item.info) for id, item in self.items()])


    def stoppedObserving(self, perspective, observer):
        self.observers.remove(observer)


    def notify(self, event, *args, **kwargs):
        # Override to provide event notification for remote observers.
        Roster.notify(self, event, *args, **kwargs)

        for observer in self.observers:
            # Event handlers are called on the next iteration of the reactor,
            # to allow the caller of this method to return a result.
            reactor.callLater(0, observer.callRemote, event, *args, **kwargs)




class RemoteRoster(Roster, pb.RemoteCache):
    """A client-side Roster, which mirrors a server-side LocalRoster object
    by tracking changes.
    """


    def setCopyableState(self, state):
        self.update(state)

