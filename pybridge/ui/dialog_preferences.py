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
from manager import wm
from pybridge.ui import settings

from pybridge.bridge.symbols import Suit

SUIT_NAMES = {Suit.Club: _("Club"), Suit.Diamond: _("Diamond"),
              Suit.Heart: _("Heart"), Suit.Spade: _("Spade") }

SUIT_SYMBOLS = {Suit.Club: u'\N{BLACK CLUB SUIT}',
                Suit.Diamond: u'\N{BLACK DIAMOND SUIT}',
                Suit.Heart: u'\N{BLACK HEART SUIT}',
                Suit.Spade: u'\N{BLACK SPADE SUIT}' }

SUIT_LABEL_TEMPLATE = "<span color=\'%s\' size=\'xx-large\'>%s</span>"


class DialogPreferences(GladeWrapper):

    glade_name = 'dialog_preferences'


    def setUp(self):
        # Allow user to select only image files for background.
        filter_pixbufs = gtk.FileFilter()
        filter_pixbufs.add_pixbuf_formats()
        filter_pixbufs.set_name(_("Image files"))
        self.background.add_filter(filter_pixbufs)

        # Build a list of card decks from which the user may choose.
        # (The user is prevented from selecting an arbitary image.)
        model = gtk.ListStore(str)
        self.cardstyle.set_model(model)
        cell = gtk.CellRendererText()
        self.cardstyle.pack_start(cell, True)
        self.cardstyle.add_attribute(cell, 'text', 0)

        activedeck = settings.appearance.get('deck', 'bonded.png')
        # Populate list of card decks.
        path = env.find_pixmap('')
        for filename in os.listdir(path):
            if filename.endswith('.png'):
                iter = model.append((filename,))
                if filename == activedeck:
                    self.cardstyle.set_active_iter(iter)


# Signal handlers.


    def on_cardstyle_changed(self, widget, *args):
        print "cardstyle changed"


    def on_background_changed(self, widget, *args):
        print "background changed"


    def on_suitcolour_clicked(self, widget, *args):
        # Get symbol in Suit corresponding to button clicked.
        suit_buttons = {self.button_clubcolour: Suit.Club,
                        self.button_diamondcolour: Suit.Diamond,
                        self.button_heartcolour: Suit.Heart,
                        self.button_spadecolour: Suit.Spade }
        suit = suit_buttons[widget]

        title = _("Select colour for %s symbol" % SUIT_NAMES[suit])
        dialog = gtk.ColorSelectionDialog(title)
        dialog.colorsel.set_current_color(gtk.gdk.color_parse('#888888'))

        def dialog_response_cb(dialog, response_id):
            if response_id == gtk.RESPONSE_OK:
                colour = dialog.colorsel.get_current_color()

                # Set button label to colour selected by user.
                label = widget.get_children()[0]
                hexrep = gtk.color_selection_palette_to_string([colour])
                label.set_markup(SUIT_LABEL_TEMPLATE % (hexrep, SUIT_SYMBOLS[suit]))

            dialog.destroy()

        dialog.connect('response', dialog_response_cb)
        #dialog.show()
        dialog.run()


    def on_cancelbutton_clicked(self, widget, *args):
        wm.close(self)


    def on_okbutton_clicked(self, widget, *args):
        print "SAVE SETTINGS"
        wm.close(self)

