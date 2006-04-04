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


from twisted.spread import pb


# Base errors.

class DeniedRequest(pb.Error):
	"""Raised in response to an unsatisfiable request."""

class IllegalRequest(pb.Error):
	"""Raised in response to an erroneous request."""


# Subclasses of DeniedRequest.

class GameHandHiddenError(DeniedRequest): pass
class GameInvalidCallError(DeniedRequest): pass
class GameInvalidCardError(DeniedRequest): pass
class GameOutOfTurnError(DeniedRequest): pass

class TableObservingError(DeniedRequest): pass
class TableNameExistsError(DeniedRequest): pass
class TableNameUnknownError(DeniedRequest): pass
class TablePlayingError(DeniedRequest): pass
class TableSeatOccupiedError(DeniedRequest): pass

class RequestUnavailableError(DeniedRequest): pass

class UserNameExistsError(DeniedRequest): pass
class UserNameUnknownError(DeniedRequest): pass


# Subclasses of IllegalRequest.

class IllegalNameError(IllegalRequest): pass

class InvalidParameterError(IllegalRequest): pass

