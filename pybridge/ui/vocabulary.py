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
A repository for translatable symbols and names.
"""

import gtk

from pybridge.bridge.symbols import *
import pybridge.bridge.call as Call

from config import config


CALLTYPE_NAMES = {
    Call.Pass: _('Pass'),
    Call.Double: _('Double'),
    Call.Redouble: _('Redouble'),
}

CALLTYPE_SYMBOLS = {
    Call.Pass: '-',
    Call.Double: 'X',
    Call.Redouble: 'XX',
}

DIRECTION_NAMES = {
    Direction.North: _('North'),
    Direction.East: _('East'),
    Direction.South: _('South'),
    Direction.West: _('West'),
}

DIRECTION_SYMBOLS = {
    Direction.North: _('N'),
    Direction.East: _('E'),
    Direction.South: _('S'),
    Direction.West: _('W'),
}

LEVEL_SYMBOLS = {
    Level.One: '1',
    Level.Two: '2',
    Level.Three: '3',
    Level.Four: '4',
    Level.Five: '5',
    Level.Six: '6',
    Level.Seven: '7',
}

RANK_NAMES = {
    Rank.Two: _('Two'),
    Rank.Three: _('Three'),
    Rank.Four: _('Four'),
    Rank.Five: _('Five'),
    Rank.Six: _('Six'),
    Rank.Seven: _('Seven'),
    Rank.Eight: _('Eight'),
    Rank.Nine: _('Nine'),
    Rank.Ten: _('Ten'),
    Rank.Jack: _('Jack'),
    Rank.Queen: _('Queen'),
    Rank.King: _('King'),
    Rank.Ace: _('Ace'),
}

RANK_SYMBOLS = {
    Rank.Two: '2',
    Rank.Three: '3',
    Rank.Four: '4',
    Rank.Five: '5',
    Rank.Six: '6',
    Rank.Seven: '7',
    Rank.Eight: '8',
    Rank.Nine: '9',
    Rank.Ten: '10',
    Rank.Jack: 'J',
    Rank.Queen: 'Q',
    Rank.King: 'K',
    Rank.Ace: 'A',
}

SUIT_NAMES = {
    Suit.Club: _('Clubs'),
    Suit.Diamond: _('Diamonds'),
    Suit.Heart: _('Hearts'),
    Suit.Spade: _('Spades'),
}

if config['Appearance'].get('SuitSymbols'):
    SUIT_SYMBOLS = {
        Suit.Club: u'\N{BLACK CLUB SUIT}',
        Suit.Diamond: u'\N{BLACK DIAMOND SUIT}',
        Suit.Heart: u'\N{BLACK HEART SUIT}',
        Suit.Spade: u'\N{BLACK SPADE SUIT}',
    }
else:
    SUIT_SYMBOLS = {
        Suit.Club: 'C',
        Suit.Diamond: 'D',
        Suit.Heart: 'H',
        Suit.Spade: 'S',
    }

STRAIN_NAMES = {
    Strain.Club: _('Club'),
    Strain.Diamond: _('Diamond'),
    Strain.Heart: _('Heart'),
    Strain.Spade: _('Spade'),
    Strain.NoTrump: _('No Trump'),
}

if config['Appearance'].get('SuitSymbols'):
    STRAIN_SYMBOLS = {
        Strain.Club: u'\N{BLACK CLUB SUIT}',
        Strain.Diamond: u'\N{BLACK DIAMOND SUIT}',
        Strain.Heart: u'\N{BLACK HEART SUIT}',
        Strain.Spade: u'\N{BLACK SPADE SUIT}',
        Strain.NoTrump: 'NT',
    }
else:
    STRAIN_SYMBOLS = {
        Strain.Club: 'C',
        Strain.Diamond: 'D',
        Strain.Heart: 'H',
        Strain.Spade: 'S',
        Strain.NoTrump: 'NT',
    }

VULN_SYMBOLS = {
    Vulnerable.All: _('All'),
    Vulnerable.NorthSouth: _('N/S'),
    Vulnerable.EastWest: _('E/W'),
    Vulnerable.None: _('None'),
}


def render_call(call):
    if isinstance(call, Call.Bid):
        if call.strain == Strain.NoTrump:  # No associated colour.
            return LEVEL_SYMBOLS[call.level] + STRAIN_SYMBOLS[Strain.NoTrump]
        else:
            rgb = config['Appearance']['Colours'].get(call.strain.key, (0, 0, 0))
            hexrep = gtk.color_selection_palette_to_string([gtk.gdk.Color(*rgb)])
            return "%s<span color=\'%s\'>%s</span>" % \
                   (LEVEL_SYMBOLS[call.level], hexrep, STRAIN_SYMBOLS[call.strain])
    else:
        return CALLTYPE_SYMBOLS[call.__class__]


def render_call_name(call):
    if isinstance(call, Call.Bid):
        return _('%(level)s %(strain)s') % {'level': LEVEL_NAMES[call.level],
                                           'strain': STRAIN_NAMES[call.strain]}
    else:
        return CALLTYPE_NAMES[call.__class__]


def render_card(card):
    rgb = config['Appearance']['Colours'].get(card.suit.key, (0, 0, 0))
    hexrep = gtk.color_selection_palette_to_string([gtk.gdk.Color(*rgb)])
    return "%s<span color=\'%s\'>%s</span>" % \
           (RANK_SYMBOLS[card.rank], hexrep, SUIT_SYMBOLS[card.suit])


def render_card_name(card):
    return _('%(rank)s of %(suit)s') % {'rank': card.rank, 'suit': card.suit}


def render_contract(contract):
    """Produce a format string representing the contract.
    
    @param contract: a contract object.
    @type contract: dict
    @return: a format string representing the contract.
    @rtype: str
    """
    doubled = contract['redoubleBy'] and CALLTYPE_SYMBOLS[Call.Redouble] \
              or contract['doubleBy'] and CALLTYPE_SYMBOLS[Call.Double] or ''

    fields = {'bid': render_call(contract['bid']), 'doubled': doubled,
              'declarer': DIRECTION_NAMES[contract['declarer']]}

    if doubled:
        return _('%(bid)s %(doubled)s by %(declarer)s') % fields
    else:
        return _('%(bid)s by %(declarer)s') % fields

