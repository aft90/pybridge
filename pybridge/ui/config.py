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
Manages PyBridge client configuration file.
"""

from StringIO import StringIO
from configobj import ConfigObj
from validate import Validator

import pybridge.environment as env

# Config spec
spec = StringIO("""# PyBridge configuration file

[Connection]
    HostAddress = string
    PortNumber = integer(0, 65535)
    Username = string
    Password = string

[Appearance]
    CardStyle = string
    BackgroundImage = string
    SuitSymbols = boolean(default=True)

    [[Colours]]
        Club = int_list(3, 3)
        Diamond = int_list(3, 3)
        Heart = int_list(3, 3)
        Spade = int_list(3, 3)

""")


config = None
val = Validator()

def load():
    global config
    filename = env.find_config_client('config')
    config = ConfigObj(filename, create_empty=True, configspec=spec)
    config.validate(val, copy=True)

def save():
    global config
    config.validate(val, copy=True)
    config.write()

