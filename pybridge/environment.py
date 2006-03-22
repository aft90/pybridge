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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import os, sys

GLADE_DIR = "glade"
PIXMAPS_DIR = "pixmaps"

class Environment:

	def __init__(self):
		currentdir = os.path.dirname(os.path.abspath(sys.argv[0]))
		basedir = os.path.abspath(os.path.join(currentdir, '..'))

		if os.path.exists(os.path.join(basedir, 'share')):
			self._data_dir = os.path.join(basedir, 'share', 'pybridge')
		else:
			self._data_dir = basedir


	def find_glade(self, name):
		return os.path.join(self._data_dir, GLADE_DIR, name)

	def find_pixmap(self, name):
		return os.path.join(self._data_dir, PIXMAPS_DIR, name)

environment = Environment()
