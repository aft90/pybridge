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


# Default settings based on the user's environment.
import locale
locale.setlocale(locale.LC_ALL, '')

import gettext, gtk.glade as glade
import pybridge.environment as env

for module in gettext, glade:
    module.bindtextdomain('pybridge', env.get_localedir())
    module.textdomain('pybridge')

# Register the gettext function for the whole interpreter as "_"
gettext.install('pybridge', env.get_localedir())


import config
config.load()


def run():
    """Starts the PyBridge client UI."""

    # Set exception hook to display error dialog.
    import sys
    from excepthook import excepthook
    sys.excepthook = excepthook

    from manager import wm
    from window_main import WindowMain
    wm.open(WindowMain)

    from twisted.python import log
    log.startLogging(sys.stdout)

    # Start the event loop.
    from twisted.internet import reactor
    reactor.run()
    import gtk
    gtk.main()

    config.save()  # Save config at exit.

