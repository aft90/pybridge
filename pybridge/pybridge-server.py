#!/usr/bin/env python

from twisted.internet import protocol, reactor

from server.protocol import ClientProtocol

BridgeFactory = protocol.ServerFactory()
BridgeFactory.protocol = ClientProtocol

# This will be replaced by a service, in time.
reactor.listenTCP(5040, BridgeFactory)
reactor.run()
