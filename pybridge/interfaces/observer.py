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


"""
Provides interfaces for the Observer Pattern.

For more information, see Gamma et al., "Design Patterns: Elements of Reusable
Object-Oriented Software", ISBN 0-201-63361-2.
"""


from zope.interface import Interface


class ISubject(Interface):
    """ISubject defines methods required for observation of an object."""


    def attach(self, observer):
        """Add observer to list of observers.
        
        @param observer: object implementing IListener.
        """


    def detach(self, observer):
        """Remove observer from list of observers.
        
        @param observer: object implementing IListener.
        """


    def notify(self, event, *args, **kwargs):
        """Inform all observers that state has been changed by event.
        
        @param event: the name of the event.
        @type event: str
        """




class IListener(Interface):
    """IListener defines methods required by observers of an ISubject."""


    def update(self, event, *args, **kwargs):
        """Called by ISubject being observed."""

