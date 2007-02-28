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

import webbrowser

from pybridge import __version__ as version
import pybridge.environment as env
from pybridge.network.client import client

from eventhandler import eventhandler
import utils

TABLE_ICON = env.find_pixmap("table.png")
USER_ICON = env.find_pixmap("user.png")


class WindowMain(GladeWrapper):

    glade_name = 'window_main'

    callbacks = ('tableOpened', 'tableClosed', 'userLoggedIn', 'userLoggedOut')

    tableview_icon = gtk.gdk.pixbuf_new_from_file_at_size(TABLE_ICON, 48, 48)
    peopleview_icon = gtk.gdk.pixbuf_new_from_file_at_size(USER_ICON, 48, 48)


    def new(self):
        self.tables = {}   # For each observed table, reference to window.
        
        # Set up table model and icon view.
        self.tableview.set_text_column(0)
        self.tableview.set_pixbuf_column(1)
        self.tableview_model = gtk.ListStore(str, gtk.gdk.Pixbuf)
        self.tableview_model.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.tableview.set_model(self.tableview_model)
        
        # Set up people model and icon view.
        # TODO: allow users to provide their own "avatar" icons.
        self.peopleview.set_text_column(0)
        self.peopleview.set_pixbuf_column(1)
        self.peopleview_model = gtk.ListStore(str, gtk.gdk.Pixbuf)
        self.peopleview_model.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.peopleview.set_model(self.peopleview_model)
        
        # Register event callbacks.
        eventhandler.registerCallbacksFor(self, self.callbacks)


    def cleanup(self):
        eventhandler.unregister(self, self.callbacks)
        for instance in self.tables.values():
            utils.windows.close('window_bridgetable', instance)


    def joinTable(self, tableid, host=False):
        
        def success(table):
            window = utils.windows.open('window_bridgetable', parent=self)
            self.tables[table.id] = window
            window.setTable(table)
            
        d = client.joinTable(tableid, host)
        d.addCallback(success)
        return d


    def leaveTable(self, tableid):
        
        def success(r):
            del self.tables[tableid]
        
        d = client.leaveTable(tableid)
        d.addCallback(success)
        return d


# Registered event handlers.


    def event_tableOpened(self, tableid):
        """Adds a table to the table listing."""
        self.tableview_model.append([tableid, self.tableview_icon])


    def event_tableClosed(self, tableid):
        """Removes a table from the table listing."""
        
        def func(model, path, iter, user_data):
            if model.get_value(iter, 0) in user_data:
                model.remove(iter)
                return True
        
        self.tableview_model.foreach(func, tableid)


    def event_userLoggedIn(self, user):
        """Adds a user to the people listing."""
        self.peopleview_model.append([user, self.peopleview_icon])


    def event_userLoggedOut(self, user):
        """Removes a user from the people listing."""
        
        def func(model, path, iter, user_data):
            if model.get_value(iter, 0) in user_data:
                model.remove(iter)
                return True
        
        self.peopleview_model.foreach(func, user)


# Signal handlers.


    def on_notebook_switch_page(self, notebook, page, page_num):
        pass


    def on_tableview_item_activated(self, iconview, path, *args):
        iter = self.tableview_model.get_iter(path)
        tableid = self.tableview_model.get_value(iter, 0)
        if tableid not in client.tables:
            self.joinTable(tableid)
            self.jointable.set_property('sensitive', False)


    def on_tableview_selection_changed(self, iconview, *args):
        cursor = self.tableview.get_cursor()
        if cursor:  # Ensure cursor contains a path, not None.
            iter = self.tableview_model.get_iter(cursor[0])  # Path.
            tableid = self.tableview_model.get_value(iter, 0)
            # If client not joined to table, enable Join Table button.
            sensitive = tableid not in client.tables
            self.jointable.set_property('sensitive', sensitive)
            # Display information about table.
            self.frame_tableinfo.set_property('sensitive', True)
            self.label_tableid.set_text(tableid)
            self.label_tabletype.set_text(client.tablesAvailable[tableid]['type'])
        else:
            self.frame_tableinfo.set_property('sensitive', False)
            self.label_tableid.set_text('')
            self.label_tabletype.set_text('')


    def on_peopleview_selection_changed(self, iconview, *args):
        cursor = self.peopleview.get_cursor()
        if cursor:  # Ensure cursor contains a path, not None.
            iter = self.peopleview_model.get_iter(cursor[0])  # Path.
            person = self.peopleview_model.get_value(iter, 0)
            # Display information about person.
            self.frame_personinfo.set_property('sensitive', True)
            self.label_personname.set_text(person)
        else:
            self.frame_personinfo.set_property('sensitive', False)
            self.label_personname.set_text('')


    def on_window_main_delete_event(self, widget, *args):
        utils.quit()
#        return True


    def on_newtable_clicked(self, widget, *args):
        if not utils.windows.get('dialog_newtable'):
            utils.windows.open('dialog_newtable', parent=self)


    def on_jointable_clicked(self, widget, *args):
        path = self.tableview.get_cursor()[0]
        self.on_tableview_item_activated(self.tableview, path)


    def on_disconnect_activate(self, widget, *args):
        client.disconnect()
        utils.windows.close(self.glade_name)
        utils.windows.open('dialog_connection')


    def on_quit_activate(self, widget, *args):
        utils.quit()


    def on_preferences_activate(self, widget, *args):
        utils.windows.open('dialog_preferences')


    def on_homepage_activate(self, widget, *args):
        webbrowser.open('http://pybridge.sourceforge.net/')


    def on_about_activate(self, widget, *args):
        about = gtk.AboutDialog()
        about.set_name('PyBridge')
        about.set_version(version)
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
        
        about.run()
        about.destroy()

