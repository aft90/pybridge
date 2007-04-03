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


from twisted.internet import gtk2reactor
gtk2reactor.install()
import gtk

from twisted.internet import reactor

import pybridge.environment as env
from pybridge.settings import Settings

import locale
import gettext
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain('pybridge', env.get_localedir())
gettext.textdomain('pybridge')
gettext.install('pybridge')

filename = env.find_config_client('client.cfg')
settings = Settings(filename, ['Connection', 'General'])


def run():
    """Starts the PyBridge client UI."""

    from manager import wm
    from window_main import WindowMain
    wm.open(WindowMain)

    # Start the event loop.
    reactor.run()
    gtk.main()

