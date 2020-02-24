import unittest

from pybridge.games.bridge.card import Card
from pybridge.games.bridge.symbols import Rank, Suit


class TestCard(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testEquality(self):
        """Testing equality of cards"""
        cards1 = [Card(r, s) for r in Rank for s in Suit]
        cards2 = [Card(r, s) for r in Rank for s in Suit]

        # Test equality of cards.
        for c1, c2 in zip(cards1, cards2):
            self.assertEqual(c1, c1)  # Same reference, same card.
            self.assertEqual(c1, c2)  # Different reference, same card.

        # Test inequality of cards.
        cards2.insert(0, cards2.pop())  # Shift by one card.
        for c1, c2 in zip(cards1, cards2):
            self.assertNotEqual(c1, c2)

        # No card is equal to any non-card object.
        self.assertNotEqual(Card(Rank.Ace, Suit.Spade), 42)


    def testCompare(self):
        """Testing comparison of cards"""

        # Test comparisons between selected cards.
        for suit in Suit:
            ace = Card(Rank.Ace, suit)
            king = Card(Rank.King, suit)
            two = Card(Rank.Two, suit)
            self.assertTrue(ace > king and ace > two and king > two)

        # Test comparisons between all cards, by sorting.
        cards = [Card(r, s) for r in Rank for s in Suit]  # Not sorted order!
        cards.sort()  # Smallest to largest.
        self.assertEqual(cards, [Card(r, s) for s in Suit for r in Rank])

