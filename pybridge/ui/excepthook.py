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


"""
Captures exceptions and displays them to user in a GTK dialog,
instead of the console which may not be visible.

Source: http://faq.pygtk.org/index.py?req=show&file=faq20.010.htp
"""

import gtk
import traceback
from StringIO import StringIO


def excepthook(type, value, tb):
    dialog = gtk.MessageDialog(parent=None, flags=gtk.DIALOG_MODAL,
                           buttons=gtk.BUTTONS_CLOSE, type=gtk.MESSAGE_WARNING)
    dialog.set_title(_('Program error'))
    dialog.set_markup(_('PyBridge detected an unexpected program error. You should close and restart PyBridge.'))
    dialog.format_secondary_markup(_('If you continue to experience this error, please submit a bug report, attaching the following error trace.'))

    # Set up display of traceback.
    textview = gtk.TextView(); textview.show()
    textview.set_editable(False)
    sw = gtk.ScrolledWindow(); sw.show()
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    sw.add(textview)
    frame = gtk.Frame();
    frame.set_shadow_type(gtk.SHADOW_IN)
    frame.add(sw)
    frame.set_border_width(6)
    dialog.vbox.add(frame)
    textbuffer = textview.get_buffer()
    trace = StringIO()
    traceback.print_exception(type, value, tb, None, trace)
    textbuffer.set_text(trace.getvalue())
    textview.set_size_request(320, 240)

    dialog.details = frame
    dialog.details.show()

    def dialog_response_cb(dialog, response_id):
        dialog.destroy()

    dialog.connect('response', dialog_response_cb)
    dialog.run()

