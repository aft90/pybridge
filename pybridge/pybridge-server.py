#!/usr/bin/env python

# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2005 PyBridge Project.
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


from twisted.internet import protocol, reactor

from server.protocol import ClientProtocol
BridgeFactory = protocol.ServerFactory()
BridgeFactory.protocol = ClientProtocol

import server.registry
registry = server.registry.getHandle()

# TODO: Replaced with a service.
reactor.listenTCP(5040, BridgeFactory)
reactor.run()

# Shut down registry, gracefully.
registry.close()
