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

Source: http://faq.pyGtk.org/index.py?req=show&file=faq20.010.htp
"""

from gi.repository import Gtk
import traceback
from io import StringIO


def exceptdialog(errormessage):
    dialog = Gtk.MessageDialog(parent=None, flags=Gtk.DialogFlags.MODAL,
                           buttons=Gtk.ButtonsType.CLOSE, type=Gtk.MessageType.WARNING)
    dialog.set_title(_('Program error'))
    dialog.set_markup(_('PyBridge detected an unexpected program error. You should close and restart PyBridge.'))
    dialog.format_secondary_markup(_('If you continue to experience this error, please submit a bug report, attaching the following error trace.'))

    # Set up display of traceback.
    textview = Gtk.TextView(); textview.show()
    textview.set_editable(False)
    sw = Gtk.ScrolledWindow(); sw.show()
    sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    sw.add(textview)
    frame = Gtk.Frame();
    frame.set_shadow_type(Gtk.ShadowType.IN)
    frame.add(sw)
    frame.set_border_width(6)
    dialog.vbox.add(frame)
    textbuffer = textview.get_buffer()
    textbuffer.set_text(errormessage)
    textview.set_size_request(320, 240)

    dialog.details = frame
    dialog.details.show()

    def dialog_response_cb(dialog, response_id):
        dialog.destroy()

    dialog.connect('response', dialog_response_cb)
    dialog.run()


def excepthook(type, value, tb):
    trace = StringIO()
    traceback.print_exception(type, value, tb, None, trace)
    exceptdialog(trace.getvalue())

