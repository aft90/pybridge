

from zope.interface import Interface


class IServerEvents(Interface):
    """IServerEvents defines methods to track the state of a server."""


    def connectionLost(self, connector, reason):
        """Called when connection to a server is lost."""


    def tableOpened(self, table):
        """Called when a new table is opened."""


    def tableClosed(self, table):
        """Called when an existing table is closed."""


    def userLoggedIn(self, user):
        """Called when a user has connected and logged in."""


    def userLoggedOut(self, user):
        """Called when a user has logged out."""

