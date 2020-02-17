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


import time
from twisted.internet import reactor
from twisted.spread import pb
from zope.interface import implements

from pybridge.interfaces.observer import ISubject, IListener
from pybridge.network.error import DeniedRequest, IllegalRequest



class Message(pb.Copyable, pb.RemoteCopy):
    """A textual message, from a sender, to any number of recipients."""


    def __init__(self, text, sender, recipients):
        self.text = text
        self.sender = sender
        self.recipients = recipients
        self.time = time.localtime()


    def getStateToCopy(self):
        state = {}
        state['text'] = self.text
        state['sender'] = self.sender.name
        state['recipients'] = [r.name for r in self.recipients]
        state['time'] = tuple(self.time)
        return state


    def setCopyableState(self, state):
        self.text = state['text']
        self.sender = state['sender']
        self.recipients = state.get('recipients', [])
        self.time = time.struct_time(state['time'])


pb.setUnjellyableForClass(Message, Message)




class Chat:  # TODO subclass observable?
    """A simple chat facility, facilitating communication between users."""

    implements(ISubject)


    def __init__(self):
        self.listeners = []

        self.messages = []  # Ordered from oldest to newest.
        self.moderators = []
        self.observers = []  # User identifiers.


    def attach(self, listener):
        self.listeners.append(listener)


    def detach(self, listener):
        self.listeners.remove(listener)


    def notify(self, event, *args, **kwargs):
        for listener in self.listeners:
            listener.update(event, *args, **kwargs)


    

class LocalChat(Chat, pb.Cacheable):

    messageMaxLength = 1000  # An upper limit on the length of messages.


    class ChatClient(pb.Viewable):
        """A front-end for client users to interact with a LocalChat object."""
    

        def __init__(self, chat):
            self.__chat = chat


        def view_sendMessage(self, user, text, recipients=[]):
            """Relays message to other users in chat.
            
            If the recipients argument is specified, only named recipients will
            receive the message as a 'whisper'. Otherwise, all users in the chat
            will recieve the 'shouted' message.
            """
            if type(text) is not str:
                raise IllegalRequest("Expected str, got %s" % type(text))
            # The user cannot be trusted to provide a valid Message object.
            message = Message(text, user, recipients)
            return self.__chat.send(message)


        def view_censor(self, user, censorUser):
            pass        


        def view_kickUser(self, user, kickUser):
            """Eject a user from the chat and prevent them from re-joining.
            
            The user must be a moderator in the Chat object.
            """
            pass


    def __init__(self):
        Chat.__init__(self)
        self.observers = {}  # User avatars mapped to RemoteChat references.
        self.view = self.ChatClient(self)


    def send(self, message):
        # Validate message.
        if message.text == '':
            raise DeniedRequest("Message must contain text")
        if len(message.text) > self.messageMaxLength:
            raise DeniedRequest("Message text longer than character limit")
        # TODO: filter message for spam, obscenity, ...

        if message.recipients:  # Specified recipients.
            sendTo = [p for p in self.observers if p.name in message.recipients]  # O(n^2)
            if sendTo == []:
                raise DeniedRequest("No named recipient present at table.")
        else:
            sendTo = list(self.observers.keys())

        self.messages.append(message)
        self.notify('gotMessage', message=message)
        # return defer.succeed(message)


    def notify(self, event, *args, **kwargs):
        Chat.notify(self, event, *args, **kwargs)
        # For all observers, calls event handler with provided arguments.
        for obs in list(self.observers.values()):
            # Event handlers are called on the next iteration of the reactor,
            # to allow the caller of this method to return a result.
            reactor.callLater(0, obs.callRemote, event, *args, **kwargs)


    def getStateToCacheAndObserveFor(self, perspective, observer):
        self.notify('addObserver', perspective.name)
        self.observers[perspective] = observer

        state = {}
        state['messages'] = []  # TODO: supply all messages?
        state['observers'] = [p.name for p in self.observers]
        state['view'] = self.view

        return state


    def stoppedObserving(self, perspective, observer):
        del self.observers[perspective]
        self.notify('removeObserver', perspective.name)




class RemoteChat(Chat, pb.RemoteCache):


    def setCopyableState(self, state):
        self.messages = state['messages']
        self.observers = state['observers']
        self.__view = state['view']


    def send(self, text):
        d = self.__view.callRemote('sendMessage', text)
        return d


    def observe_gotMessage(self, message):
        self.messages.append(message)
        self.notify('gotMessage', message)


    def observe_addObserver(self, observer):
        self.observers.append(observer)
        self.notify('addObserver', observer)


    def observe_removeObserver(self, observer):
        self.observers.remove(observer)
        self.notify('removeObserver', observer)


pb.setUnjellyableForClass(LocalChat, RemoteChat)

