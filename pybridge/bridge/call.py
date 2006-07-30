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


from twisted.spread import pb

from pybridge.enum import Enum

# Bid levels.
Level = Enum('One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven')

# Bid strains, or denominations.
Strain = Enum('Club', 'Diamond', 'Heart', 'Spade', 'NoTrump')


class Call(pb.Copyable, pb.RemoteCopy):
	"""Superclass for bids, passes, doubles and redoubles."""


	def __str__(self):
		return str(self.__class__)


class Pass(Call): pass

class Double(Call): pass

class Redouble(Call): pass


class Bid(Call):


	def __init__(self, level, strain):
		assert(level in Level)
		assert(strain in Strain)
		self.level = level
		self.strain = strain


	def __cmp__(self, other):
		if isinstance(other, Bid):  # Comparing two bids.
			selfVal = self.level.index*len(Strain) + self.strain.index
			otherVal = other.level.index*len(Strain) + other.strain.index
			return cmp(selfVal, otherVal)
		else:  # Comparing non-bid calls returns true.
			return 1


	def __str__(self):
		return "%s %s" % (self.level, self.strain)


	def getStateToCopy(self):
		return {'level' : str(self.level),
		        'strain' : str(self.strain), }


	def setCopyableState(self, state):
		self.level = getattr(Level, state['level'])
		self.strain = getattr(Strain, state['strain'])

