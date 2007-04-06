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


class LocalUserManager(LocalRoster):


    def userLogin(self, user):
        self[user.name] = user
        self.notify('userLogin', username=user.name, info=user.info)


    def userLogout(self, user):
        del self[user.name]
        self.notify('userLogout', username=user.name)



class RemoteUserManager(RemoteRoster):


    def observe_userLogin(self, username, info):
        self[username] = info
        self.notify('userLogin', username=username, info=info)


    def observe_userLogout(self, username):
        del self[username]
        self.notify('userLogout', username=username)

