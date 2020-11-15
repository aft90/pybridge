import unittest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import gi
gi.require_version('Gtk', '3.0')

from pybridge.games.bridge.symbols import Rank, Suit, Level, Strain, Direction
import pybridge.games.bridge.call as Call
from pybridge.games.bridge.auction import Contract
from pybridge.ui.vocabulary import render_call, render_contract, rgba_hexrep


class TestVocabulary(unittest.TestCase):


    def test_render_call_nt(self):
        call = Mock(spec=Call.Bid)
        call.level = Level.Two
        call.strain = Strain.NoTrump
        self.assertEqual('2NT', render_call(call))

    def test_render_call_suit_with_initial(self):
        call = Mock(spec=Call.Bid)
        call.level = Level.Two
        call.strain = Strain.Diamond
        with patch('pybridge.ui.vocabulary.config', { 'Appearance' : { 'Colours': {'Diamond': (0,0,0)}} }), patch('pybridge.ui.vocabulary.STRAIN_SYMBOLS', { Strain.Diamond: 'D' }):
            self.assertEqual("2<span color='#000000000000'>D</span>", render_call(call))

    def test_render_call_suit_with_symbol(self):
        call = Mock(spec=Call.Bid)
        call.level = Level.Two
        call.strain = Strain.Diamond
        with patch('pybridge.ui.vocabulary.config', { 'Appearance': { 'Colours': {'Diamond': (0,0,0) } } }), patch('pybridge.ui.vocabulary.STRAIN_SYMBOLS', { Strain.Diamond: '\N{BLACK DIAMOND SUIT}'}) :
            self.assertEqual("2<span color='#000000000000'>\N{BLACK DIAMOND SUIT}</span>", render_call(call))

    def test_render_contract_undoubled(self):
        contract = Mock(spec=Contract)
        contract.doubleBy = False
        contract.redoubleBy = False
        call = Mock(spec=Call.Bid)
        call.level = Level.Four
        call.strain = Strain.Spade
        contract.declarer = Direction.North
        contract.bid = call
        with patch('pybridge.ui.vocabulary.config', { 'Appearance' : { 'Colours': {'Spade': (0,0,0)}} }), patch('pybridge.ui.vocabulary.STRAIN_SYMBOLS', { Strain.Spade: 'S' }):
            self.assertEqual("4<span color='#000000000000'>S</span> by North", render_contract(contract))

    def test_render_contract_doubled(self):
        contract = Mock(spec=Contract)
        contract.doubleBy = True
        contract.redoubleBy = False
        call = Mock(spec=Call.Bid)
        call.level = Level.Six
        call.strain = Strain.NoTrump
        contract.declarer = Direction.South
        contract.bid = call
        self.assertEqual("6NT X by South", render_contract(contract))

    def test_render_contract_redoubled(self):
        contract = Mock(spec=Contract)
        contract.doubleBy = False
        contract.redoubleBy = True
        call = Mock(spec=Call.Bid)
        call.level = Level.Three
        call.strain = Strain.Heart
        contract.declarer = Direction.East
        contract.bid = call
        with patch('pybridge.ui.vocabulary.config', { 'Appearance' : { 'Colours': {'Heart': (0,0,0)}} }), patch('pybridge.ui.vocabulary.STRAIN_SYMBOLS', { Strain.Heart: 'H' }):
            self.assertEqual("3<span color='#000000000000'>H</span> XX by East", render_contract(contract))

    def test_redoubled_takes_precedence_over_doubled(self):
        contract = Mock(spec=Contract)
        contract.doubleBy = True
        contract.redoubleBy = True
        call = Mock(spec=Call.Bid)
        call.level = Level.Two
        call.strain = Strain.NoTrump
        contract.declarer = Direction.West
        contract.bid = call
        self.assertEqual("2NT XX by West", render_contract(contract))


    def test_rgba_hexrep(self):
        black = self.mock_rgba(0., 0., 0.)
        white = self.mock_rgba(1., 1., 1.)
        red = self.mock_rgba(1., 0., 0.)
        lime = self.mock_rgba(0.5411764705882353, 0.8862745098039215, 0.20392156862745098)
        self.assertEqual('#000000000000', rgba_hexrep(black))
        self.assertEqual('#ffffffffffff', rgba_hexrep(white))
        self.assertEqual('#ffff00000000', rgba_hexrep(red))
        self.assertEqual('#8a8ae2e23434', rgba_hexrep(lime))

    def mock_rgba(self, r, g, b):
        m = MagicMock(spec=['red', 'green', 'blue'])
        type(m).red = r
        type(m).green = g
        type(m).blue = b
        return m