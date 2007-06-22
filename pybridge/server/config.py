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


"""
Manages PyBridge server configuration file.
"""

from StringIO import StringIO
from configobj import ConfigObj
from validate import Validator

import pybridge.environment as env

# Config spec
spec = StringIO("""# PyBridge server configuration file

[Database]
    Engine = option('sqlite', 'sapdb', 'postgresql', 'firebird', 'maxdb', 'sybase', 'interbase', 'psycopg', 'mysql', 'mssql', 'postgres', default='sqlite')
    DatabaseName = string  # Or path to database file if using sqlite.
    User = string  # Not used with sqlite.
    Password = string  # Not used with sqlite.
    Host = string  # Leave empty for localhost.
    Port = integer  # Leave empty for default.
""")


config = None
val = Validator()

def load():
    global config
    filename = env.find_config_server('server.cfg')
    config = ConfigObj(filename, create_empty=True, configspec=spec)
    config.validate(val, copy=True)

def save():
    global config
    config.validate(val, copy=True)
    config.write()

