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


from gi.repository import Gtk

from pybridge.network.client import client

from .eventhandler import SimpleEventHandler
from .manager import WindowManager, wm
from .wrapper import ICON_PATH

from .window_chat import WindowChat


class WindowGameTable:
    """A generic table display window.
    
    This exposes core table functionality to the user, and may be subclassed to
    support individual games.
    """

    gametype = _('Unnamed Game')


    def __init__(self, parent=None):
        self.window = Gtk.Window()
        if parent:
            self.set_transient_for(parent.window)
        self.window.connect('delete_event', self.on_window_delete_event)
        self.window.set_icon_from_file(ICON_PATH)
        self.window.set_title(_('Table'))

        self.setUp()
        self.window.show_all()


    def setUp(self):
        self.children = WindowManager()  # Private to this window.
        self.eventHandler = SimpleEventHandler(self)

        self.player = None
        self.position = None
        self.table = None  # Table currently displayed in window.

        # Set up widget layout.
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toolbar = Gtk.Toolbar()
        self.toolbar.set_style(Gtk.ToolbarStyle.BOTH_HORIZ)
        vbox.pack_start(self.toolbar, False, True, 0)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.gamearea = Gtk.Viewport()  # Use self.gamearea.add(...)
        hbox.pack_start(self.gamearea, True, True, 0)
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)  # Use self.sidebar.pack_start(..., True, True, 0)
        self.sidebar.set_border_width(6)
        hbox.pack_start(self.sidebar, False, True, 0)
        vbox.pack_start(hbox, True, True, 0)
        self.statusbar = Gtk.Statusbar()
        vbox.pack_start(self.statusbar, False, True, 0)
        self.window.add(vbox)

        # Set up toolbar buttons.
        self.takeseat = Gtk.MenuToolButton(icon_widget=Gtk.Image.new_from_icon_name('media-playback-start', Gtk.IconSize.LARGE_TOOLBAR))
        self.takeseat.set_label(_('Take Seat'))
        self.takeseat.set_is_important(True)
        self.takeseat.connect('clicked', self.on_takeseat_clicked)
        self.toolbar.insert(self.takeseat, -1)

        self.leaveseat = Gtk.ToolButton(icon_widget=Gtk.Image.new_from_icon_name('media-playback-stop', Gtk.IconSize.LARGE_TOOLBAR))
        self.leaveseat.set_label(_('Leave Seat'))
        self.leaveseat.connect('clicked', self.on_leaveseat_clicked)
        self.leaveseat.set_property('sensitive', False)
        self.toolbar.insert(self.leaveseat, -1)

        self.toolbar.insert(Gtk.SeparatorToolItem(), -1)

        self.fullscreen = Gtk.ToggleToolButton(icon_widget=Gtk.Image.new_from_icon_name('view-fullscreen', Gtk.IconSize.LARGE_TOOLBAR))
        self.fullscreen.set_label(_('Full Screen'))
        self.fullscreen.connect('clicked', self.on_fullscreen_clicked)
        self.toolbar.insert(self.fullscreen, -1)

        self.leavetable = Gtk.ToolButton(icon_widget=Gtk.Image.new_from_icon_name('application-exit', Gtk.IconSize.LARGE_TOOLBAR))
        self.leavetable.set_label(_('Leave Table'))
        self.leavetable.connect('clicked', self.on_leavetable_clicked)
        self.toolbar.insert(self.leavetable, -1)

        self.toolbar.insert(Gtk.SeparatorToolItem(), -1)


    def tearDown(self):
        # Close all child windows.
        for window in list(self.children.values()):
            self.children.close(window)

        # If table has chat session, remove it from chat window.
        if self.table.chat:
            chatwin = wm.get(WindowChat)
            if chatwin:
                chatwin.removeChat(self.table.chat)

        self.table = None  # Dereference table.


    def errback(self, failure):
        # TODO: display error in window.
        print("Error: %s" % failure.getErrorMessage())
        print(failure.getBriefTraceback())


    def setTable(self, table):
        """Set display to follow specified table object.
        
        @param table: the focal table.
        """
#        if self.table:
#            self.table.detach(self.eventHandler)
        self.table = table
        self.table.attach(self.eventHandler)

        fields = {'tablename': self.table.id, 'gametype': self.gametype}
        title = _('%(tablename)s (%(gametype)s)') % fields
        self.window.set_title(title)

        if self.table.chat:
            chatwin = wm.get(WindowChat) or wm.open(WindowChat)
            chatwin.addChat(self.table.chat, title=title)


# Registered event handlers.


# Signal handlers.


    def on_takeseat_clicked(self, widget, position):
        # Subclasses should override this method, and call it using super(...)
        # with the position argument guaranteed to be specified.
        assert position is not None

        self.takeseat.set_property('sensitive', False)

        def success(player):
            self.leaveseat.set_property('sensitive', True)
            self.player = player
            self.position = position

        def failure(reason):
            self.takeseat.set_property('sensitive', True)  # Re-enable.

        d = self.table.joinGame(position)
        d.addCallbacks(success, failure)
        return d


    def on_leaveseat_clicked(self, widget, *args):
        self.leaveseat.set_property('sensitive', False)

        def success(r):
            self.takeseat.set_property('sensitive', True)
            self.player = None
            self.position = None

        def failure(reason):
            self.leaveseat.set_property('sensitive', True)  # Re-enable.

        d = self.table.leaveGame(self.position)
        d.addCallbacks(success, failure)
        return d


    def on_leavetable_clicked(self, widget, *args):
        # If user is currently playing a game, request confirmation.
        if self.player and self.table.game.inProgress():
            dialog = Gtk.MessageDialog(parent=self.window,
                                       flags=Gtk.DialogFlags.MODAL,
                                       type=Gtk.MessageType.QUESTION)
            dialog.set_title(_('Leave table?'))
            dialog.add_button('_Cancel', Gtk.ResponseType.CANCEL)
            dialog.add_button(_('Leave Table'), Gtk.ResponseType.OK)
            dialog.set_markup(_('Are you sure you wish to leave this table?'))
            dialog.format_secondary_text(_('You are currently playing a game. Leaving may forfeit the game, or incur penalties.'))

            def dialog_response_cb(dialog, response_id):
                dialog.destroy()
                if response_id == Gtk.ResponseType.OK:
                    d = client.leaveTable(self.table.id)
                    d.addCallbacks(lambda _: wm.close(self), self.errback)

            dialog.connect('response', dialog_response_cb)
            dialog.show()

        else:
            d = client.leaveTable(self.table.id)
            d.addCallbacks(lambda _: wm.close(self), self.errback)


    def on_fullscreen_clicked(self, widget, *args):
        if self.fullscreen.get_active():
            self.window.fullscreen()
        else:
            self.window.unfullscreen()


    def on_window_delete_event(self, widget, *args):
        self.on_leavetable_clicked(widget, *args)
        return True  # Stops window deletion taking place.

