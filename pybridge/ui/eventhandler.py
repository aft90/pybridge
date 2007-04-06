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


from zope.interface import implements

from pybridge.interfaces.observer import IListener


class SimpleEventHandler:
    """An implementation of IListener which redirects updates to its target."""

    implements(IListener)


    def __init__(self, target, prefix='event_'):
        self.__target = target
        self.__prefix = prefix


    def update(self, event, *args, **kwargs):
        """Redirects named event to target's handler method, if present."""
        method = getattr(self.__target, "%s%s" % (self.__prefix, event), None)
        if method:
            method(*args, **kwargs)

