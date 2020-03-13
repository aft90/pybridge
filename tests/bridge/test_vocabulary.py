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
