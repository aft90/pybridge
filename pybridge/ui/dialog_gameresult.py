# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2006 PyBridge Project.
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

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import gtk
from wrapper import GladeWrapper

from pybridge.network.client import client
import utils


class DialogGameresult(GladeWrapper):

    glade_name = 'dialog_gameresult'


    def new(self):
        pass


    def setup(self, message):
        self.label_result.set_text(message)


# Signal handlers.


    def on_leavetable_clicked(self, widget, *args):
        d = client.leaveTable(self.parent.table.id)
        d.addCallback(lambda _: self.parent.leftTable(self.parent.table))
        utils.closeWindow('dialog_gameresult')


    def on_nextdeal_clicked(self, widget, *args):
        utils.closeWindow('dialog_gameresult')


    def on_dialog_gameresult_delete_event(self, widget, *args):
        return True  # Stops window deletion taking place.

