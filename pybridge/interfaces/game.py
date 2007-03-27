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


class IGame(Interface):
    """IGame defines methods common to all games.
    
    This interface makes no assumptions about the game to be played, besides
    that it has players.
    """


    def start(self, initial):
        """Called to initialise game state. This resets any previous state.
        
        @param initial: the initial state of the game.
        """


    def getState(self):
        """Returns an object representing the current state of the game.
        This may be used to export a game to be saved or transmitted.

        @return: a state object.
        """


    def setState(self, state):
        """Overwrites the current game state with the specified state.
        This may be used to import a saved or transmitted game.

        @param state: a state object.
        """


    def updateState(self, event, *args, **kwargs):
        """Updates game state in response to event.
        
        @param event: the name of the event.
        """


    def addPlayer(self, position):
        """Provide caller with a Player object bound to position.
        
        The specified position must be vacant.
        
        @param position: position to add player.
        @return: a Player object.
        """


    def removePlayer(self, position):
        """Removes player from specified position.
        
        @param position: position from which to remove player.
        """


# Methods to query game state.


    def inProgress(self):
        """Indicates whether the game is currently being played or has finished.
        
        @return: True if game is running, False otherwise.
        """


class ICardGame(IGame):
    """ICardGame defines methods specific to card games.
    
    ICardGame inherits all methods in IGame.
    """


    def getHand(self, position):
        """Returns a list of the known cards in hand.
        For each unknown card, None is used as its placeholder.
        
        @player: a player identifier.
        @return: the hand of the player.
        """


    def getTurn(self):
        """If game is in progress, returns the player who is next to play.
        
        @return: a player identifier, or None.
        """

