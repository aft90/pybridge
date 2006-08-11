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
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import os, sys

HOME = os.path.expanduser('~')

if hasattr(sys, 'frozen'):  # For py2exe distribution.
    CURRENTDIR = os.path.dirname(sys.executable)
    BASEDIR = os.path.abspath(CURRENTDIR)
else:
    CURRENTDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    BASEDIR = os.path.abspath(os.path.join(CURRENTDIR, '..'))

if os.path.exists(os.path.join(BASEDIR, 'share', 'pybridge')):
    DATADIR = os.path.join(BASEDIR, 'share', 'pybridge')
else:
    DATADIR = BASEDIR

CONFIG_DIR = os.path.join(HOME, '.pybridge')
CLIENT_SETTINGS_PATH = os.path.join(CONFIG_DIR, 'client.cfg')
USER_DB = os.path.join(CONFIG_DIR, 'users.db')

if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

LOCALE_DIR = os.path.join(BASEDIR, 'locale')

DOCS_DIR = '.'
GLADE_DIR = 'glade'
PIXMAPS_DIR = 'pixmaps'


class Environment:

    def find_datafile(self, name):
        return os.path.join(CONFIG_DIR, name)

    def find_doc(self, name):
        return os.path.join(DATADIR, DOCS_DIR, name)

    def find_glade(self, name):
        return os.path.join(DATADIR, GLADE_DIR, name)

    def find_pixmap(self, name):
        return os.path.join(DATADIR, PIXMAPS_DIR, name)


environment = Environment()

