import unittest
import random

from pybridge.bridge.bidding import Bidding
from pybridge.bridge.call import Bid, Pass, Double, Redouble
from pybridge.bridge.symbols import Direction, Level, Strain


class TestBidding(unittest.TestCase):


    # Generate some bids.
    bids = [Bid(l, s) for l in Level for s in Strain]


    def setUp(self):
        dealer = random.choice(Direction)
        self.bidding = Bidding(dealer)


    def tearDown(self):
        self.bidding = None


    def testGetCurrentCall(self):
        """getCurrentCall"""
        for calltype in [Bid, Pass, Double, Redouble]:
            self.assertEqual(self.bidding.getCurrentCall(calltype), None)

        for call, calltype in [(Pass(), Pass), (Bid(Level.One, Strain.Club), Bid),
                               (Double(), Double), (Redouble(), Redouble)]:
            self.assertEqual(self.bidding.getCurrentCall(calltype), None)
            self.bidding.makeCall(call)
            self.assertEqual(self.bidding.getCurrentCall(calltype), call)

        # A bid should clear types Pass, Double, Redouble.
        bid = Bid(Level.One, Strain.Diamond)
        self.bidding.makeCall(bid)
        self.assertEqual(self.bidding.getCurrentCall(Bid), bid)
        for calltype in [Pass, Double, Redouble]:
            self.assertEqual(self.bidding.getCurrentCall(calltype), None)
        

    def testWhoseTurn(self):
        """whoseTurn"""
        # Tests whoseTurn() before and after making calls.
        turn = Direction[self.bidding.dealer.index]
        for call in self.bids:
            self.assertEqual(self.bidding.whoseTurn(), turn)
            self.bidding.makeCall(call)
            turn = Direction[(turn.index + 1) % 4]
            self.assertEqual(self.bidding.whoseTurn(), turn)


    def testIsValidCall(self):
        """isValidCall"""
        pass


def main():
    suite = unittest.makeSuite(TestBidding)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()

