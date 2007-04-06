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


from roster import LocalRoster, RemoteRoster


class LocalTableManager(LocalRoster):


    def openTable(self, table):
        # TODO: don't notify clients which don't recognise game type.
        self[table.id] = table
        self.notify('openTable', tableid=table.id, info=table.info)


    def closeTable(self, table):
        del self[table.id]
        self.notify('closeTable', tableid=table.id)




class RemoteTableManager(RemoteRoster):


    def observe_openTable(self, tableid, info):
        self[tableid] = info
        self.notify('openTable', tableid=tableid, info=info)


    def observe_closeTable(self, tableid):
        del self[tableid]
        self.notify('closeTable', tableid=tableid)

