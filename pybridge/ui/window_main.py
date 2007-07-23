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


import gtk
from wrapper import GladeWrapper

from twisted.internet import reactor
import webbrowser

from pybridge import __version__ as PYBRIDGE_VERSION
from pybridge.games import SUPPORTED_GAMES
import pybridge.environment as env
from pybridge.network.client import client

from eventhandler import SimpleEventHandler
from manager import wm

from dialog_connection import DialogConnection
from dialog_newtable import DialogNewtable
from dialog_preferences import DialogPreferences
from dialog_userinfo import DialogUserInfo
from window_gametable import WindowGameTable

# TODO: import all Window*Table classes automatically.
from pybridge.games.bridge.ui.window_bridgetable import WindowBridgeTable

TABLE_ICON = env.find_pixmap("table.png")
USER_ICON = env.find_pixmap("user.png")


class WindowMain(GladeWrapper):

    glade_name = 'window_main'

    tableview_icon = gtk.gdk.pixbuf_new_from_file_at_size(TABLE_ICON, 48, 48)
    userview_icon = gtk.gdk.pixbuf_new_from_file_at_size(USER_ICON, 48, 48)


    def setUp(self):
        # Set up table model and icon view.
        self.tableview.set_text_column(0)
        self.tableview.set_pixbuf_column(1)
        model = gtk.ListStore(str, gtk.gdk.Pixbuf)
        model.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.tableview.set_model(model)

        # Set up user model and icon view.
        self.userview.set_text_column(0)
        self.userview.set_pixbuf_column(1)
        model = gtk.ListStore(str, gtk.gdk.Pixbuf)
        model.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.userview.set_model(model)

        # Attach event handler to listen for events.
        self.eventHandler = SimpleEventHandler(self)
        client.attach(self.eventHandler)

        if not wm.get(DialogConnection):
            wm.open(DialogConnection, parent=self)


    def tearDown(self):
        # TODO: detach event handler from all attached subjects.

        # Close all windows.
        for window in wm.values():
            wm.close(window)
        client.disconnect()


    def quit(self):
        """Shut down gracefully."""
        client.detach(self.eventHandler)
        wm.close(self)
        reactor.stop()
        gtk.main_quit()


    def errback(self, failure):
        print "Error: %s" % failure.getErrorMessage()
        print failure.getTraceback()


# Event handlers.


    def event_loggedIn(self, username):
        self.notebook.set_property('sensitive', True)
        self.menu_connect.set_property('visible', False)
        self.menu_disconnect.set_property('visible', True)
        self.menu_newtable.set_property('sensitive', True)
        self.newtable.set_property('sensitive', True)


    def event_loggedOut(self):
        for window in wm.values():
            if isinstance(window, WindowGameTable):
                wm.close(window)

        self.notebook.set_property('sensitive', False)
        self.menu_connect.set_property('visible', True)
        self.menu_disconnect.set_property('visible', False)
        self.menu_newtable.set_property('sensitive', False)
        #self.newtable.set_property('sensitive', False)

        self.tableview.get_model().clear()
        self.userview.get_model().clear()


    def event_connectionLost(self, host, port):
        dialog = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL,
                                   type=gtk.MESSAGE_ERROR)
        dialog.set_title(_('Connection to server lost'))
        dialog.set_markup(_('The connection to %s was lost unexpectedly.' % host))
        dialog.format_secondary_text(_('Please check your computer\'s network connection status before reconnecting. If you cannot reconnect, the server may be offline.'))
        # If this problem persists...

        def dialog_response_cb(dialog, response_id):
            dialog.destroy()
            if response_id == gtk.RESPONSE_OK:
                wm.open(DialogConnection, parent=self)

        dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        dialog.add_button(gtk.STOCK_CONNECT, gtk.RESPONSE_OK)

        dialog.connect('response', dialog_response_cb)
        dialog.show()


    def event_gotRoster(self, name, roster):
        lookup = {'tables' : (self.tableview.get_model(), self.tableview_icon),
                  'users' : (self.userview.get_model(), self.userview_icon)}

        try:
            model, icon = lookup[name]
            for id, info in roster.items():
                model.append([id, icon])
            roster.attach(self.eventHandler)
        except KeyError:
            pass  # Ignore an unrecognised roster.


    def event_openTable(self, tableid, info):
        """Adds a table to the table listing."""
        # Only display table if it supported by client.
        if info['gamename'] in SUPPORTED_GAMES:
            self.tableview.get_model().append([tableid, self.tableview_icon])


    def event_closeTable(self, tableid):
        """Removes a table from the table listing."""
        
        def func(model, path, iter, user_data):
            if model.get_value(iter, 0) in user_data:
                model.remove(iter)
                return True

        model = self.tableview.get_model()
        model.foreach(func, tableid)


    def event_userLogin(self, username, info):
        """Adds a user to the people listing."""
        self.userview.get_model().append([username, self.userview_icon])


    def event_userLogout(self, username):
        """Removes a user from the people listing."""
        
        def func(model, path, iter, user_data):
            if model.get_value(iter, 0) in user_data:
                model.remove(iter)
                return True

        model = self.userview.get_model()
        model.foreach(func, username)


# Signal handlers.


    def on_notebook_switch_page(self, notebook, page, page_num):
        pass


    def on_tableview_item_activated(self, iconview, path, *args):

        def joinedTable(table):
            # TODO: select correct table window class.
            window = wm.open(WindowBridgeTable, id=tableid)
            window.setTable(table)

        model = self.tableview.get_model()
        iter = model.get_iter(path)
        tableid = model.get_value(iter, 0)
        if tableid not in client.tables:
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
            w = wm.open(DialogUserInfo, winid)
            w.setUserInfo(username, info)

        if not wm.get(winid):
            # TODO: if user info in cache, do not request again from server.
            d = client.getUserInformation(username)
            d.addCallback(gotUserInfo)


    def on_userview_selection_changed(self, iconview, *args):
        cursor = self.userview.get_cursor()
        if cursor:  # Ensure cursor contains a path, not None.
            self.buttonbox_users.set_property('sensitive', True)
        else:
            self.buttonbox_users.set_property('sensitive', False)


    def on_window_main_delete_event(self, widget, *args):
        self.quit()


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
        if len([True for w in wm.values() if isinstance(w, WindowGameTable) and w.player]) > 0:
            dialog = gtk.MessageDialog(parent=self.window,
                                       flags=gtk.DIALOG_MODAL,
                                       type=gtk.MESSAGE_QUESTION)
            dialog.set_title(_('Disconnect from server'))
            dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            dialog.add_button(gtk.STOCK_DISCONNECT, gtk.RESPONSE_OK)
            dialog.set_markup(_('Are you sure you wish to disconnect?'))
            dialog.format_secondary_text(_('You are playing at a table. Disconnecting may forfeit the game, or incur penalties.'))

            do_disconnect = (dialog.run() == gtk.RESPONSE_OK)
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
        about = gtk.AboutDialog()
        about.set_name('PyBridge')
        about.set_version(PYBRIDGE_VERSION)
        about.set_copyright('Copyright (C) 2004-2007 Michael Banks')
        about.set_comments(_('A free online bridge game.'))
        about.set_website('http://pybridge.sourceforge.net/')
        license = file(env.find_doc('COPYING')).read()
        about.set_license(license)
        authorsfile = file(env.find_doc('AUTHORS'))
        authors = [author.strip() for author in authorsfile]
        about.set_authors(authors)
        logo_path = env.find_pixmap('pybridge.png')
        logo = gtk.gdk.pixbuf_new_from_file(logo_path)
        about.set_logo(logo)

        def dialog_response_cb(dialog, response_id):
            dialog.destroy()

        about.connect('response', dialog_response_cb)
        about.show()

