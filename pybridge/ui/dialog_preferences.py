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
import os
from wrapper import GladeWrapper

import pybridge.environment as env
import utils


class DialogPreferences(GladeWrapper):

    glade_name = 'dialog_preferences'


    def new(self):
        model = gtk.ListStore(str)
        self.carddeck.set_model(model)
        cell = gtk.CellRendererText()
        self.carddeck.pack_start(cell, True)
        self.carddeck.add_attribute(cell, 'text', 0)
        # Populate list of card decks.
        path = env.find_pixmap('')
        for filename in os.listdir(path):
            if filename.endswith('.png'):
                iter = model.append((filename,))
                if filename == 'bonded.png':
                    self.carddeck.set_active_iter(iter)


# Signal handlers.


    def on_carddeck_changed(self, widget, *args):
        print "changed"


    def on_cancelbutton_clicked(self, widget, *args):
        print "cancel"
        utils.windows.close(self.glade_name)


    def on_okbutton_clicked(self, widget, *args):
        print "ok"
        utils.windows.close(self.glade_name)

