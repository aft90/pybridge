import unittest

from pybridge.games.bridge.deck import Deck


class TestDeck(unittest.TestCase):


    def setUp(self):
        self.deck = Deck()


    def tearDown(self):
        self.deck = None


    def testRandomDeal(self):
        """Testing randomDeal"""
        for i in range(100):
            deal = self.deck.randomDeal()
            self.assert_(self.deck.isValidDeal(deal))


    def testDealToIndex(self):
        """Testing dealToIndex (assuming indexToDeal correct)"""
        n = 1
        while n < self.deck.D:
            deal = self.deck.indexToDeal(n)
            pn = self.deck.dealToIndex(deal)
            self.assertEqual(n, pn)
            n = n*2 + 1


    def testIndexToDeal(self):
        """Testing indexToDeal (assuming dealToIndex and isValidDeal correct)"""
        n = 1
        while n < self.deck.D:
            deal = self.deck.indexToDeal(n)
            self.assert_(self.deck.isValidDeal(deal))
            pn = self.deck.dealToIndex(deal)
            self.assertEqual(n, pn)
            n = n*2 + 1


def main():
    suite = unittest.makeSuite(TestDeck)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()

