import unittest
from unittest.mock import Mock, patch

from pybridge.games.bridge.symbols import Rank, Suit, Level, Strain, Direction
import pybridge.games.bridge.call as Call
from pybridge.games.bridge.auction import Contract
from pybridge.ui.vocabulary import render_call, render_contract

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
