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


from zope.interface import Interface


class ITable(Interface):
    """ITable defines methods which are common to all table implementations,
    which are expected to provide the following services:
    
    - Synchronisation of game state between the server and connected clients.
      This should be transparent to game code.
    
    - Functionality shared by all games, such as:
    
        - Game management: players joining and leaving the game, closure of
          table when all observers have left.
        
        - Communication between users.
    
    A table is the abstraction of "the place where a game is played".
    """


    def joinGame(self, user, position):
        """Registers a user as an active player, provided that the specified
        position is vacant.
        
        The interface supports a single user playing at multiple positions.
        Implementations may disable this feature.
        
        @param user: user identifier.
        @param position: position which player takes.
        """


    def leaveGame(self, user, position):
        """Removes player from their position.
        
        Specification of position is required, if the user is playing at
        multiple positions.
        
        @param user: user identifier.
        @param position: position which player takes.
        """


    def sendMessage(self, message, sender, recipients):
        """Issues message from sender to all named recipients,
        or to all observers.
        
        @param message: message text string.
        @param sender: user identifier of sender.
        @param recipients: user identifiers of recipient observers.
        """

