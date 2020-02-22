# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2009 PyBridge Project.
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


import hashlib
from twisted.cred import credentials
from twisted.internet import reactor
from twisted.python import log
from twisted.spread import pb
from zope.interface import implementer

from pybridge import __version__ as CLIENT_VERSION

from pybridge.interfaces.observer import ISubject

from pybridge.network.localtable import LocalTable
from pybridge.network.remotetable import RemoteTable
pb.setUnjellyableForClass(LocalTable, RemoteTable)

from pybridge.network.tablemanager import LocalTableManager, RemoteTableManager
from pybridge.network.usermanager import LocalUserManager, RemoteUserManager
pb.setUnjellyableForClass(LocalTableManager, RemoteTableManager)
pb.setUnjellyableForClass(LocalUserManager, RemoteUserManager)


# TODO: this class should be split into:
#   - a factory class which establishes connections with servers
#   - a class which represents connections (and implements ISubject) 

@implementer(ISubject)
class NetworkClient:
    """Provides the glue between the client code and the server."""

    def __init__(self):
        self.listeners = []

        self.avatar = None  # Remote avatar reference.
        self.factory = pb.PBClientFactory()
        self.factory.clientConnectionLost = self.connectionLost

        self.expectLoseConnection = False  # Indicates when disconnecting.

        self.username = None
        self.serverVersion = None
        self.tables = {}  # Tables observed.
        self.tableRoster = None
        self.userRoster = None


    def connectionLost(self, connector, reason):
        log.msg("Lost connection to server")

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
            log.msg("Lost connection: %s" % reason.getErrorMessage())
            self.notify('connectionLost', host=connector.host,
                                          port=connector.port)


    def errback(self, failure):
        log.err("Error: %s" % failure.getErrorMessage())
        return failure  # Pass through for next error handler.


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
        """Drops connection to server cleanly."""
        self.expectLoseConnection = True  # Suppress "Lost Connection" error.
        self.factory.disconnect()


    def login(self, username, password):
        """Authenticate to connected server with username and password.
        
        @param username:
        @param password:

        The SHA-1 hash of the password string is transmitted, protecting
        the user's password from eavesdroppers.
        """

        def gotServerVersion(version):
            self.serverVersion = version

        def gotRoster(roster, name):
            if name == 'tables':
                self.tableRoster = roster
            elif name == 'users':
                self.userRoster = roster
            self.notify('gotRoster', name=name, roster=roster)

        def connectedAsRegisteredUser(avatar):
            """Actions to perform when connection succeeds."""
            self.avatar = avatar
            self.username = username
            self.notify('loggedIn', username=username)
            
            # Report client version number to server.
            d = avatar.callRemote('setClientVersion', CLIENT_VERSION)
            d.addCallbacks(gotServerVersion, self.errback)

            # Request services from server.
            for rostername in ['tables', 'users']:
                d = avatar.callRemote('getRoster', rostername)
                d.addCallbacks(gotRoster, self.errback, callbackArgs=[rostername])

        # Generate a SHA-1 hash of password
        pw_hash = self.__hashPass(password)
        creds = credentials.UsernamePassword(username.encode('utf-8'), pw_hash.encode('utf-8'))
        d = self.factory.login(creds, client=None)
        d.addCallbacks(connectedAsRegisteredUser, self.errback)

        return d


    def register(self, username, password):
        """Register user account on connected server."""

        def connectedAsAnonymousUser(avatar):
            """Register user account on server."""
            pw_hash = self.__hashPass(password)
            d = avatar.callRemote('register', username, pw_hash)
            # TODO: after registration, need to disconnect from server?
            return d

        anon = credentials.UsernamePassword(b'', b'')
        d = self.factory.login(anon, client=None)
        d.addCallbacks(connectedAsAnonymousUser, self.errback)

        return d


# Client request methods.


    def changePassword(self, password):
        """Change password of user account.
        
        @param password: the new password.
        """
        pw_hash = self.__hashPass(password)
        d = self.avatar.callRemote('changePassword', pw_hash)
        return d


    def joinTable(self, tableid, gameclass=None, host=False):

        def success(table):
            self.tables[tableid] = table
            self.notify('joinTable', tableid=tableid, table=table)
            return table

        params = {}
        if host:
            params['gamename'] = gameclass.__name__

        d = self.avatar.callRemote('joinTable', tableid, host, **params)
        d.addCallbacks(success, self.errback)
        return d


    def leaveTable(self, tableid):

        def success(r):
            del self.tables[tableid]
            self.notify('leaveTable', tableid=tableid)

        d = self.avatar.callRemote('leaveTable', tableid)
        d.addCallbacks(success, self.errback)
        return d


    def getUserInformation(self, username):
        # TODO: cache user information once retrieved.
        d = self.avatar.callRemote('getUserInformation', username)
        return d


    def __hashPass(self, password):
        """Generates a SHA-1 hash of supplied password."""
        # TODO: may want to salt the hash with username, but this breaks backward compatibility.
        return hashlib.sha1(password.encode('utf-8')).hexdigest()


client = NetworkClient()

