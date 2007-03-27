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


class DeniedRequest(pb.Error):
    """Raised by server in response to an unsatisfiable request from client."""


class IllegalRequest(pb.Error):
    """Raised by server in response to an erroneous request from client.
    
    The propagation of this error from server to client suggests there is a bug
    in the client code (ie. sending invalid or ill-formatted data to the server)
    or in the server code (ie. mishandling data).
    
    Please report any bugs which you discover in PyBridge!
    """


class GameError(pb.Error):
    """Raised by game in response to an unsatisfiable or erroneous request."""

