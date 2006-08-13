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


from UserDict import UserDict
from twisted.spread import pb


class LocalTableManager(UserDict, pb.Cacheable):
    """Information that the server provides to all connected clients.
    
    """


    def __init__(self):
        UserDict.__init__(self)
        self.observers = []


    def getStateToCacheAndObserveFor(self, perspective, observer):
        self.observers.append(observer)
        
        # TODO: iterate through tables and pull out information.
        state = {}
        for tableid in self.keys():
            state[tableid] = {'type' : 'bridge'}
        
        return state


    def stoppedObserving(self, perspective, observer):
        self.observers.remove(observer)

    
    def openTable(self, table):
        self[table.id] = table
        state = {'type' : 'bridge'}
        self.updateObservers('tableOpened', tableid=table.id, info=state)


    def closeTable(self, table):
        del self[table.id]
        self.updateObservers('tableClosed', tableid=table.id)


# Utility methods.


    def updateObservers(self, event, **kwargs):
        """For each observer, calls event handler with provided kwargs."""
        for observer in self.observers:
            observer.callRemote(event, **kwargs)




class RemoteTableManager(UserDict, pb.RemoteCache):
    """Maintains a cache of a server-side LocalTableManager object.

    """


    def setCopyableState(self, state):
        self.update(state)


    def setEventHandler(self, handler):
        self.eventHandler = handler


# Remote update methods.


    def observe_tableOpened(self, tableid, info):
        self[tableid] = info
        self.eventHandler.tableOpened(tableid)


    def observe_tableClosed(self, tableid):
        del self[tableid]
        self.eventHandler.tableClosed(tableid)

