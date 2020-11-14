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


from gi.repository import Gtk, Pango, Gdk
import time

from .eventhandler import SimpleEventHandler
from .manager import wm
from .wrapper import ICON_PATH


class PeopleBox(Gtk.Box):
    """An embeddable list of people."""

    __gtype_name__ = 'PeopleBox'


    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.people_count_label = Gtk.Label()
        self.pack_start(self.people_count_label, False, True, 0)

        self.people = {}  # Maps TreeIter objects to people.
        self.people_store = Gtk.ListStore(str)
        self.people_list = Gtk.TreeView()
        self.people_list.set_model(self.people_store)
        self.people_list.set_headers_visible(False)
        column = Gtk.TreeViewColumn(None, Gtk.CellRendererText(), text=0)
        self.people_store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.people_list.append_column(column)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.add(self.people_list)
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.IN)
        frame.add(sw)
        frame.set_border_width(6)
        self.pack_start(frame, True, True, 0)


    def add(self, person):
        iter = self.people_store.append([person])
        self.people[person] = iter
        self._set_people_count_label()


    def remove(self, person):
        iter = self.people[person]
        self.people_store.remove(iter)
        del self.people[person]
        self._set_people_count_label()


    def _set_people_count_label(self):
        count = len(self.people)
        if count == 1:
            text = _('1 person in room')
        else:
            text = _('%(num)s people in room') % {'num': count}
        self.people_count_label.set_text(text)




class ChatBox(Gtk.VPaned):
    """An embeddable chat box widget, compatible with Chat objects.
    
    The design of this widget is modelled on Pidgin (http://pidgin.im/).
    """

    __gtype_name__ = 'ChatBox'

    texttags = {'username': {'weight': Pango.Weight.BOLD},
                'status': {'foreground': '#0000ff',
                           'style': Pango.Style.ITALIC},
               }


    def __init__(self):
        super().__init__()

        self.chat = None  # A Chat object to monitor.
        self.eventHandler = SimpleEventHandler(self)

        hpaned = Gtk.HPaned()
        # Conversation display.
        self.conversation = Gtk.TextView()
        self.conversation.set_editable(False)
        self.conversation.set_cursor_visible(False)
        self.conversation.set_wrap_mode(Gtk.WrapMode.WORD)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)  # Vertical scroll.
        sw.add(self.conversation)
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.IN)
        frame.add(sw)
        frame.set_border_width(6)
        hpaned.pack1(frame, resize=True, shrink=False)
        # People list display.
        self.people = PeopleBox()
        hpaned.pack2(self.people, resize=False, shrink=True)
        self.pack1(hpaned, resize=True, shrink=True)

        self.textentry = Gtk.TextView()
        self.textentry.set_editable(True)
        self.textentry.set_property('sensitive', False)
        self.textentry.set_wrap_mode(Gtk.WrapMode.WORD)
        #self.textentry.set_size_request(30, 30)
        self.textentry.connect('key_press_event', self.on_textentry_key_pressed)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.add(self.textentry)
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.IN)
        frame.add(sw)
        frame.set_border_width(6)
        self.pack2(frame, resize=True, shrink=True)

        # Populate conversation textview with text tags.
        tagtable = self.conversation.get_buffer().get_tag_table()
        for tagname, tagattrs in list(self.texttags.items()):
            tag = Gtk.TextTag(name=tagname)
            for attrname, attrvalue in list(tagattrs.items()):
                tag.set_property(attrname, attrvalue)
            tagtable.add(tag)

        self.show_all()


    def setChat(self, chat):
        if self.chat:
            self.chat.detach(self.eventHandler)
        self.chat = chat
        self.chat.attach(self.eventHandler)

        # Populate conversation display.
        buffer = self.conversation.get_buffer()
        # Clear buffer.
        start, end = buffer.get_bounds()
        buffer.delete(start, end)
        for message in self.chat.messages:
            self.display_message(message)

        # Populate people list.
        #self.people.clear()
        for person in self.chat.observers:
            self.people.add(person)

        self.textentry.set_property('sensitive', True)


    def display_message(self, message, scroll=False):
        buffer = self.conversation.get_buffer()
        if buffer.get_char_count() > 0:
            buffer.insert(buffer.get_end_iter(), '\n')

        # TODO: use client's clock, or time given by server?
        timestr = time.strftime('(%H:%M:%S)', message.time)
        buffer.insert_with_tags_by_name(buffer.get_end_iter(),
                                        timestr + ' ')

        buffer.insert_with_tags_by_name(buffer.get_end_iter(),
                                        message.sender + ':', 'username')

        buffer.insert_with_tags_by_name(buffer.get_end_iter(),
                                        ' ' + message.text)

        if scroll:  # Ensure message is visible in conversation view.
            self.conversation.scroll_to_mark(buffer.get_insert(), 0, False, 0.5, 0.5)


    def display_status(self, user, userjoins=True):
        buffer = self.conversation.get_buffer()
        if buffer.get_char_count() > 0:
            buffer.insert(buffer.get_end_iter(), '\n')

        if userjoins:
            text = _('%(user)s has joined the conversation') % {'user': user}
        else:
            text = _('%(user)s has left the conversation') % {'user': user}

        buffer.insert_with_tags_by_name(buffer.get_end_iter(), text, 'status')


# Event handlers.


    def event_gotMessage(self, message):
        self.display_message(message, scroll=True)


    def event_addObserver(self, observer):
        self.display_status(observer, userjoins=True)
        self.people.add(observer)


    def event_removeObserver(self, observer):
        self.display_status(observer, userjoins=False)
        self.people.remove(observer)


# Signal handlers.


    def on_textentry_key_pressed(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            buffer = self.textentry.get_buffer()
            start, end = buffer.get_bounds()
            text = buffer.get_text(start, end, True)
            if text:  # Don't send a blank message.
                buffer.delete(start, end)  # Clear buffer.
                self.chat.send(text)
            return True  # Inhibit self.textentry from displaying newline.
        return False




class WindowChat:
    """A tabbed display of chat sessions."""


    def __init__(self, parent=None):
        self.window = Gtk.Window()
        if parent:
            self.set_transient_for(parent.window)
        self.window.connect('delete_event', self.on_window_delete_event)
        self.window.set_icon_from_file(ICON_PATH)
        self.window.set_size_request(320, 240)  # A reasonable minimum?

        self.setUp()
        self.window.show_all()


    def setUp(self):
        self.eventHandler = SimpleEventHandler(self)
        self.chatboxes = {}  # Maps Chat objects to their ChatBox instances.

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.connect('switch-page', self.on_switch_page)
        self.window.add(self.notebook)
        self.window.set_border_width(4)


    def tearDown(self):
       # Dereference all Chat objects in chatboxes.
        for chatbox in self.chatboxes:
            chatbox.chat = None
        self.chatboxes.clear()  # Dereference Chat objects used as keys.


    def addChat(self, chat, title):
        chatbox = ChatBox()
        chatbox.setChat(chat)
        self.notebook.insert_page(chatbox, Gtk.Label(label=title), -1)
        self.chatboxes[chat] = chatbox


    def removeChat(self, chat):
        chatbox = self.chatboxes[chat]
        num = self.notebook.page_num(chatbox)
        self.notebook.remove_page(num)
        del self.chatboxes[chat]

        # If no remaining chat sessions, close window.
        if not self.chatboxes:
            wm.close(self)


    def on_switch_page(self, widget, page, page_num, *args):
        # Note the page parameter is a GPointer and not usable within PyGTK.
        page = self.notebook.get_nth_page(page_num)
        title = self.notebook.get_tab_label_text(page)
        self.window.set_title(_('Chat') + ': ' + title)


    def on_window_delete_event(self, widget, *args):
        return True  # Stops window deletion taking place.

