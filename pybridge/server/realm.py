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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from twisted.cred import checkers, portal
from twisted.spread import pb

from user import User, AnonymousUser


class Realm:

    __implements__ = portal.IRealm


    def requestAvatar(self, avatarId, mind, *interfaces):
        if pb.IPerspective not in interfaces:
            raise NotImplementedError
        
        if avatarId == checkers.ANONYMOUS:
            avatar = AnonymousUser()
            avatar.server = self.server  # Provide reference to server.
            return pb.IPerspective, avatar, lambda:None
        else:
            avatar = User(avatarId)
            avatar.server = self.server  # Provide reference to server.
            avatar.attached(mind)
            return pb.IPerspective, avatar, lambda a=avatar:a.detached(mind)

