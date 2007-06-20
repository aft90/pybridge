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


import sha
from twisted.cred import credentials
from twisted.internet import reactor
from twisted.spread import pb
from zope.interface import implements

from pybridge.interfaces.observer import ISubject

from pybridge.network.localtable import LocalTable
from pybridge.network.remotetable import RemoteTable
pb.setUnjellyableForClass(LocalTable, RemoteTable)

from pybridge.network.tablemanager import LocalTableManager, RemoteTableManager
from pybridge.network.usermanager import LocalUserManager, RemoteUserManager
pb.setUnjellyableForClass(LocalTableManager, RemoteTableManager)
pb.setUnjellyableForClass(LocalUserManager, RemoteUserManager)



class NetworkClient(pb.Referenceable):
    """Provides the glue between the client code and the server."""

    implements(ISubject)


    def __init__(self):
        self.listeners = []

        self.avatar = None  # Remote avatar reference.
        self.factory = pb.PBClientFactory()
        self.factory.clientConnectionLost = self.connectionLost

        self.expectLoseConnection = False  # Indicates when disconnecting.

        self.username = None
        self.tables = {}  # Tables observed.
        self.tableRoster = None
        self.userRoster = None


    def connectionLost(self, connector, reason):
        if self.avatar:
            # Reset invalidated remote references.
            self.avatar = None
            self.tables.clear()
            self.tableRoster.clear()
            self.userRoster.clear()
        self.username = None

        self.notify('loggedOut')

        if not self.expectLoseConnection:
            # Connection lost unexpectedly, so notify user.
            print "Lost connection: %s" % reason.getErrorMessage()
            self.notify('connectionLost', host=connector.host,
                                          port=connector.port)


    def errback(self, failure):
        print "Error: %s" % failure.getErrorMessage()


# Implementation of ISubject.


    def attach(self, listener):
        self.listeners.append(listener)


    def detach(self, listener):
        self.listeners.remove(listener)


    def notify(self, event, *args, **kwargs):
        for listener in self.listeners:
            listener.update(event, *args, **kwargs)


# Methods


    def connect(self, host, port):
        """Connect to server.

        @param host: the host name or IP address of the server.
        @type host: string
        @param port: the port number on which the server is listening.
        @type port: int
        """
        connector = reactor.connectTCP(host, port, self.factory)
        self.expectLoseConnection = False


    def disconnect(self):
        """Drops connection to server."""
        self.expectLoseConnection = True
        self.factory.disconnect()


    def login(self, username, password):
        """Authenticate to connected server with username and password.
        
        @param username:
        @param password:

        The SHA-1 hash of the password string is transmitted, protecting
        the user's password from eavesdroppers.
        """

        def gotRoster(roster, name):
            if name == 'tables':
                self.tableRoster = roster
            elif name == 'users':
                self.userRoster = roster
            self.notify('gotRoster', name=name, roster=roster)

        def connectedAsUser(avatar):
            """Actions to perform when connection succeeds."""
            self.avatar = avatar
            self.username = username
            self.notify('loggedIn', username=username)

            # Request services from server.
            for rostername in ['tables', 'users']:
                d = avatar.callRemote('getRoster', rostername)
                d.addCallbacks(gotRoster, self.errback, callbackArgs=[rostername])

        hash = sha.new(password).hexdigest()
        creds = credentials.UsernamePassword(username, hash)
        d = self.factory.login(creds, client=self)
        d.addCallback(connectedAsUser)

        return d


    def register(self, username, password):
        """Register user account on connected server."""

        def connectedAsAnonymousUser(avatar):
            """Register user account on server."""
            hash = sha.new(password).hexdigest()
            d = avatar.callRemote('register', username, hash)
            # TODO: after registration, need to disconnect from server?
            return d

        anon = credentials.UsernamePassword('', '')
        d = self.factory.login(anon, client=None)
        d.addCallback(connectedAsAnonymousUser)

        return d


# Client request methods.


    def joinTable(self, tableid, host=False):

        def success((table, remote)):
            table.master = remote  # Set RemoteReference for RemoteBridgeTable.
            self.tables[tableid] = table
            self.notify('joinTable', tableid=tableid, table=table)
            return table

        if host:
            d = self.avatar.callRemote('hostTable', tableid=tableid,
                                       tabletype='bridge')
        else:
            d = self.avatar.callRemote('joinTable', tableid=tableid)
        d.addCallback(success)
        return d


    def leaveTable(self, tableid):

        def success(r):
            del self.tables[tableid]
            self.notify('leaveTable', tableid=tableid)

        d = self.avatar.callRemote('leaveTable', tableid=tableid)
        d.addCallback(success)
        return d


client = NetworkClient()

