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


from gi.repository import Gtk, GdkPixbuf
from .wrapper import GladeWrapper

from twisted.internet import reactor
import webbrowser

from pybridge import __version__ as PYBRIDGE_VERSION
from pybridge.games import SUPPORTED_GAMES
import pybridge.environment as env
from pybridge.network.client import client

from .eventhandler import SimpleEventHandler
from .excepthook import exceptdialog
from .manager import wm

from .dialog_connection import DialogConnection
from .dialog_newtable import DialogNewtable
from .dialog_preferences import DialogPreferences
from .dialog_userinfo import DialogUserInfo
from .window_gametable import WindowGameTable

# TODO: import all Window*Table classes automatically.
from pybridge.games.bridge.ui.window_bridgetable import WindowBridgeTable

TABLE_ICON = env.find_pixmap('table.png')
USER_ICON = env.find_pixmap('user.png')


class WindowMain(GladeWrapper):

    glade_name = 'window_main'

    table_icon = GdkPixbuf.Pixbuf.new_from_file_at_size(TABLE_ICON, 48, 48)
    user_icon = GdkPixbuf.Pixbuf.new_from_file_at_size(USER_ICON, 48, 48)


    def setUp(self):
        # Track iters in ListStore objects, for O(1) lookups.
        self.tableview_iters, self.userview_iters = {}, {}
        # Set up tableview and userview.
        for view in self.tableview, self.userview:
            view.set_text_column(0)
            view.set_pixbuf_column(1)
            model = Gtk.ListStore(str, GdkPixbuf.Pixbuf)
            model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
            view.set_model(model)

        # Attach event handler to listen for events.
        self.eventHandler = SimpleEventHandler(self)
        client.attach(self.eventHandler)

        if not wm.get(DialogConnection):
            wm.open(DialogConnection, parent=self)


    def tearDown(self):
        client.disconnect()
        client.detach(self.eventHandler)
        # Terminate.
        reactor.stop()
        Gtk.main_quit()


    def quit(self):
        """Shut down gracefully."""
        # TODO: if playing a game, ensure that user really wants to quit.
        wm.close(self)  # Triggers tearDown.


    def errback(self, failure):
        message = "Network error: %s\n\n%s" % (failure.getErrorMessage(),
                                               failure.getTraceback())
        exceptdialog(message)


# Event handlers.


    def event_loggedIn(self, username):
        self.notebook.set_property('sensitive', True)
        self.menu_connect.set_property('visible', False)
        self.menu_disconnect.set_property('visible', True)
        self.menu_newtable.set_property('sensitive', True)

        self.newtable.set_property('sensitive', True)
        self.jointable.set_property('sensitive', False)
        self.userinfo_button.set_property('sensitive', False)


    def event_loggedOut(self):
        for window in list(wm.values()):
            if isinstance(window, WindowGameTable):
                wm.close(window)

        self.notebook.set_property('sensitive', False)
        self.menu_connect.set_property('visible', True)
        self.menu_disconnect.set_property('visible', False)
        self.menu_newtable.set_property('sensitive', False)

        self.tableview.get_model().clear(); self.tableview_iters.clear()
        self.userview.get_model().clear(); self.userview_iters.clear()


    def event_connectionLost(self, host, port):
        dialog = Gtk.MessageDialog(parent=self.window, flags=Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.ERROR)
        dialog.set_title(_('Connection to server lost'))
        dialog.set_markup(_('The connection to %s was lost unexpectedly.' % host))
        dialog.format_secondary_text(_('Please check your computer\'s network connection status before reconnecting. If you cannot reconnect, the server may be offline.'))
        # If this problem persists...

        def dialog_response_cb(dialog, response_id):
            dialog.destroy()
            if response_id == Gtk.ResponseType.OK:
                wm.open(DialogConnection, parent=self)

        dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.add_button(Gtk.STOCK_CONNECT, Gtk.ResponseType.OK)

        dialog.connect('response', dialog_response_cb)
        dialog.show()


    def event_gotRoster(self, name, roster):
        lookup = {'tables' : (self.tableview.get_model(), self.table_icon, self.tableview_iters),
                  'users' : (self.userview.get_model(), self.user_icon, self.userview_iters)}
        try:
            model, icon, view_iters = lookup[name]
            for id, info in list(roster.items()):
                iter = model.append([id, icon])
                view_iters[id] = iter
            roster.attach(self.eventHandler)
        except KeyError:
            pass  # Ignore an unrecognised roster.


    def event_openTable(self, tableid, info):
        # Only display table if it supported by client.
        if info['gamename'] in SUPPORTED_GAMES:
            model = self.tableview.get_model()
            iter = model.append([tableid, self.table_icon])
            self.tableview_iters[tableid] = iter


    def event_closeTable(self, tableid):
        iter = self.tableview_iters.get(tableid)
        if iter:
            model = self.tableview.get_model()
            model.remove(iter)
            del self.tableview_iters[tableid]


    def event_userLogin(self, username, info):
        model = self.userview.get_model()
        iter = model.append([username, self.user_icon])
        self.userview_iters[username] = iter


    def event_userLogout(self, username):
        iter = self.userview_iters.get(username)
        if iter:
            model = self.userview.get_model()
            model.remove(iter)
            del self.userview_iters[username]


# Signal handlers.


    def on_notebook_switch_page(self, notebook, page, page_num):
        pass


    def on_tableview_item_activated(self, iconview, path, *args):
        model = self.tableview.get_model()
        iter = model.get_iter(path)
        tableid = model.get_value(iter, 0)

        def joinedTable(table):
            # TODO: select correct table window class.
            window = wm.open(WindowBridgeTable, id=tableid)
            window.setTable(table)

        if tableid not in client.tables:  # Already joined table?
            d = client.joinTable(tableid)
            d.addCallbacks(joinedTable, self.errback)
            self.jointable.set_property('sensitive', False)


    def on_tableview_selection_changed(self, iconview, *args):
        cursor = self.tableview.get_cursor()
        if cursor:  # Ensure cursor contains a path, not None.
            model = self.tableview.get_model()
            iter = model.get_iter(cursor[0])  # Path.
            tableid = model.get_value(iter, 0)
            # If client not joined to table, enable Join Table button.
            sensitive = tableid not in client.tables
            self.jointable.set_property('sensitive', sensitive)
        else:
            self.jointable.set_property('sensitive', False)


    def on_userview_item_activated(self, iconview, path, *args):
        model = self.userview.get_model()
        iter = model.get_iter(path)
        username = model.get_value(iter, 0)

        # Allow one DialogUserInfo instance for each user.
        winid = (DialogUserInfo, username)

        def gotUserInfo(info):
            w = wm.open(DialogUserInfo, id=winid)
            w.setUserInfo(username, info)

        if not wm.get(winid):
            d = client.getUserInformation(username)
            d.addCallback(gotUserInfo)


    def on_userview_selection_changed(self, iconview, *args):
        cursor = self.userview.get_cursor()
        # If cursor contains a path, enable User Info button.
        self.userinfo_button.set_property('sensitive', bool(cursor))


    def on_newtable_clicked(self, widget, *args):
        if not wm.get(DialogNewtable):
            wm.open(DialogNewtable)


    def on_jointable_clicked(self, widget, *args):
        path = self.tableview.get_cursor()[0]
        self.on_tableview_item_activated(self.tableview, path)


    def on_userinfo_clicked(self, widget, *args):
        path = self.userview.get_cursor()[0]
        self.on_userview_item_activated(self.userview, path)


    def on_connect_activate(self, widget, *args):
        if not wm.get(DialogConnection):
            wm.open(DialogConnection)


    def on_disconnect_activate(self, widget, *args):
        do_disconnect = True

        # TODO: avoid introspection of table windows.
        if len([True for w in list(wm.values()) if isinstance(w, WindowGameTable) and w.player]) > 0:
            dialog = Gtk.MessageDialog(parent=self.window,
                                       flags=Gtk.DialogFlags.MODAL,
                                       type=Gtk.MessageType.QUESTION)
            dialog.set_title(_('Disconnect from server'))
            dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
            dialog.add_button(Gtk.STOCK_DISCONNECT, Gtk.ResponseType.OK)
            dialog.set_markup(_('Are you sure you wish to disconnect?'))
            dialog.format_secondary_text(_('You are playing at a table. Disconnecting may forfeit the game, or incur penalties.'))

            do_disconnect = (dialog.run() == Gtk.ResponseType.OK)
            dialog.destroy()

        if do_disconnect:
            # Close all table windows, triggers stoppedObserving() on all tables.
            # TODO: should do this on_disconnected
            client.disconnect()


    def on_quit_activate(self, widget, *args):
        self.quit()


    def on_preferences_activate(self, widget, *args):
        if not wm.get(DialogPreferences):
            wm.open(DialogPreferences)


    def on_homepage_activate(self, widget, *args):
        webbrowser.open('http://pybridge.sourceforge.net/')


    def on_about_activate(self, widget, *args):
        about = Gtk.AboutDialog()
        about.set_name('PyBridge')
        about.set_version(PYBRIDGE_VERSION)
        about.set_copyright('Copyright (C) 2004-2007 Michael Banks')
        about.set_comments(_('A free online bridge game.'))
        about.set_website('http://pybridge.sourceforge.net/')
        with open(env.find_doc('COPYING'), 'r') as f:
            about.set_license(f.read())
        with open(env.find_doc('AUTHORS'), 'r') as f:
            about.set_authors([author.strip() for author in f])
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file(env.find_pixmap('pybridge.png')))


        def dialog_response_cb(dialog, response_id):
            dialog.destroy()

        about.connect('response', dialog_response_cb)
        about.show()


    def on_delete_event(self, widget, *args):
        self.quit()
        return True  # Stops window deletion taking place.

