# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2005 PyBridge Project.
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


from wrapper import WindowWrapper


class WindowTables(WindowWrapper):

	window_name = 'window_tables'

	def new(self):
		self.room_tree_model = gtk.TreeStore(str, str, str)
		self.room_tree.set_model(self.room_tree_model)
		self.model_iter = self.room_tree_model.insert_after(parent = None, sibling = None)

