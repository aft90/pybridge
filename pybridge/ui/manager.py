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


from wrapper import GladeWrapper


class WindowManager(dict):
    """A dictionary with features for managing GladeWrapper window instances."""


    def open(self, windowclass, id=None, parent=None):
        """Creates a new instance of a GladeWrapper window.
        
        @param windowclass: a subclass of GladeWrapper.
        @type windowclass: classobj
        @param id: if specified, an identifier for the window instance.
        @type id: str or None
        @param parent: if specified, a parent window to set as transient.
        @type parent: GladeWrapper instance or None
        @return: the instance variable of the created window.
        @rtype: GladeWrapper instance
        """
        id = id or windowclass
        if self.get(id):
            raise KeyError, "Identifier \'%s\' already registered" % id

        instance = windowclass(parent)
        self[id] = instance
        return instance


    def close(self, instance):
        """Closes an existing instance of a GladeWrapper window.
        
        @param id: the window instance.
        @type id: instance
        """
        if instance not in self.values():
            raise ValueError, "Window instance not registered"

        # Identify the window instance.
        for id, inst in self.items():
            if inst == instance:
                break

        # Since a window may close itself, it is necessary to remove the
        # reference before invoking tearDown(), to prevent an infinite loop.
        del self[id]

        instance.tearDown()
        instance.window.destroy()


# An instance of WindowManager to be shared by all windows.
wm = WindowManager()

