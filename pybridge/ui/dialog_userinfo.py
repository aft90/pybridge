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


import gi
from gi.repository import Gtk, Pango

from .manager import wm
from .wrapper import GladeWrapper


class DialogUserInfo(GladeWrapper):

    glade_name = 'dialog_userinfo'

    fields = [('realname', _('Real Name')),
              ('email', _('Email Address')),
              ('country', ('Country')),
              ('profile', _('Profile'))]

    texttags = {'heading': {'weight': Pango.Weight.BOLD},
                'value': {},
                'value-unknown': {'foreground': 'gray'},
               }


    def setUp(self):
        self.userinfo.set_size_request(320, 160)

        # Populate information textview with text tags.
        tagtable = self.userinfo.get_buffer().get_tag_table()
        for tagname, tagattrs in list(self.texttags.items()):
            tag = Gtk.TextTag(name=tagname)
            for attrname, attrvalue in list(tagattrs.items()):
                tag.set_property(attrname, attrvalue)
            tagtable.add(tag)


    def setUserInfo(self, username, info):
        self.label_userinfo.set_markup("<span size='large'><b>%s</b></span>" %
                            _('Information for %(user)s') % {'user': username})

        # Populate information textview.
        buffer = self.userinfo.get_buffer()

        # Display recognised fields in order.
        for id, title in self.fields:
            buffer.insert_with_tags_by_name(buffer.get_end_iter(), title, 'heading')
            buffer.insert(buffer.get_end_iter(), ': ')

            value = info.get(id)
            if value:
                buffer.insert_with_tags_by_name(buffer.get_end_iter(), value, 'value')
            else:
                buffer.insert_with_tags_by_name(buffer.get_end_iter(), _('not specified'), 'value-unknown')

            buffer.insert(buffer.get_end_iter(), '\n')


    def on_closebutton_clicked(self, widget, *args):
        wm.close(self)


    def on_delete_event(self, widget, *args):
        self.on_closebutton_clicked(widget, *args)

