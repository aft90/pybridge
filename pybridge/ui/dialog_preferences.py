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
from config import config
from manager import wm
from vocabulary import *

from pybridge.bridge.symbols import Suit

SUIT_LABEL_TEMPLATE = "<span color=\'%s\' size=\'x-large\'>%s</span>"


class DialogPreferences(GladeWrapper):

    glade_name = 'dialog_preferences'


    def setUp(self):
        # Allow user to select only PNG images for background.
        filter_pixbufs = gtk.FileFilter()
        #filter_pixbufs.add_pixbuf_formats()
        filter_pixbufs.add_pattern('*.png')
        filter_pixbufs.set_name(_('PNG images'))
        self.background.add_filter(filter_pixbufs)

        # Build a list of card decks from which the user may choose.
        # (The user is prevented from selecting an arbitary image.)
        activedeck = config['Appearance'].get('CardStyle', 'bonded.png')
        model = gtk.ListStore(str)
        self.cardstyle.set_model(model)
        cell = gtk.CellRendererText()
        self.cardstyle.pack_start(cell, True)
        self.cardstyle.add_attribute(cell, 'text', 0)
        # Populate list of card decks.
        path = env.find_pixmap('')
        for filename in os.listdir(path):
            if filename.endswith('.png'):
                iter = model.append((filename,))
                if filename == activedeck:
                    self.cardstyle.set_active_iter(iter)

        # Retrieve selected background.
        background_file = config['Appearance'].get('Background')
        if background_file is None or not os.path.exists(background_file):
            background_file = env.find_pixmap('baize.png')
        self.background.set_filename(background_file)

        # Retrieve suit colours.
        self.suit_colours = {}
        for suit in Suit:
            rgb = config['Appearance']['Colours'].get(suit.key, (0, 0, 0))
            colour = gtk.gdk.Color(*rgb)
            self.suit_colours[suit] = colour
            # Set button label colour from self.suit_colours.
            hexrep = gtk.color_selection_palette_to_string([colour])
            label = getattr(self, 'label_%scolour' % suit.key.lower())
            label.set_markup(SUIT_LABEL_TEMPLATE % (hexrep, SUIT_SYMBOLS[suit]))

        use_suitsymbols = config['Appearance'].get('SuitSymbols')
        self.check_suitsymbols.set_active(use_suitsymbols)


# Signal handlers.


    def on_cardstyle_changed(self, widget, *args):
        pass


    def on_background_changed(self, widget, *args):
        pass


    def on_suitcolour_clicked(self, widget, *args):
        # Get symbol in Suit corresponding to button clicked.
        suit = [s for s in Suit if s.key.lower() in widget.get_name()][0]

        title = _("Select colour for %s symbol" % SUIT_NAMES[suit])
        dialog = gtk.ColorSelectionDialog(title)
        dialog.colorsel.set_current_color(self.suit_colours[suit])

        def dialog_response_cb(dialog, response_id):
            if response_id == gtk.RESPONSE_OK:
                colour = dialog.colorsel.get_current_color()
                self.suit_colours[suit] = colour
                # Set button label to colour selected by user.
                hexrep = gtk.color_selection_palette_to_string([colour])
                label = getattr(self, 'label_%scolour' % suit.key.lower())
                label.set_markup(SUIT_LABEL_TEMPLATE % (hexrep, SUIT_SYMBOLS[suit]))

            dialog.destroy()

        dialog.connect('response', dialog_response_cb)
        dialog.run()  # show()


    def on_cancelbutton_clicked(self, widget, *args):
        wm.close(self)


    def on_okbutton_clicked(self, widget, *args):
        # Save preferences to config file.

        for suit, colour in self.suit_colours.items():
            rgb = (colour.red, colour.green, colour.blue)
            config['Appearance']['Colours'][suit.key] = rgb

        config['Appearance']['Background'] = self.background.get_filename()

        model = self.cardstyle.get_model()
        iter = self.cardstyle.get_active_iter()
        config['Appearance']['CardStyle'] = model.get_value(iter, 0)

        config['Appearance']['SuitSymbols'] = self.check_suitsymbols.get_active()

        wm.close(self)

