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


import ConfigParser


class Settings:
    """A wrapper for ConfigParser."""


    def __init__(self, path, sections):
        """Make section key/value pairs into attributes of this object.
        
        @param path: the location of configuration file to load.
        @param sections: a list of section names to be made available.
        """
        self._path = path
        self._config = ConfigParser.SafeConfigParser()
        self._config.read(path)

        for section in sections:
            # Create sections if they do not exist.
            if not self._config.has_section(section):
                self._config.add_section(section)
            # Make items in section available as 
            items = {}
            for key, value in self._config.items(section):
                items[key] = value
            setattr(self, section.lower(), items)  # self.<section> = items


    def save(self):
        """Writes contents of section/item dicts back to file."""
        for section in self._config.sections():
            for key, value in getattr(self, section.lower()).items():
                self._config.set(section, key, value)
        self._config.write(file(self._path, 'w'))

