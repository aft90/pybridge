#!/usr/bin/env python

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

# Determine the base directory.
currentdir = os.path.dirname(os.path.abspath(sys.argv[0]))
basedir = os.path.abspath(os.path.join(currentdir, '..'))

# Find the Python module path, relative to the base directory.
if os.path.exists(os.path.join(basedir, 'lib')):
	pythonpath = os.path.join(basedir, 'lib', 'python%d.%d' % sys.version_info[:2], 'site-packages')
else:
	pythonpath = basedir

sys.path.insert(0, pythonpath)


from pybridge.client.ui import GtkGladeUI

client = GtkGladeUI()
client.run()
