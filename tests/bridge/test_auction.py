import unittest

from pybridge.games.bridge.auction import Auction
from pybridge.games.bridge.call import Bid, Pass, Double, Redouble
from pybridge.games.bridge.symbols import Direction, Level, Strain


class TestAuction(unittest.TestCase):

#    bids = [Bid(l, s) for l in Level for s in Strain]

    dealer = Direction.North
    calls = [Pass(), Pass(), Bid(Level.One, Strain.Club), Double(),
             Redouble(), Pass(), Pass(), Bid(Level.One, Strain.NoTrump),
             Pass(), Bid(Level.Three, Strain.NoTrump), Pass(), Pass(),
             Pass()]


    def setUp(self):
        self.auction = Auction(dealer=self.dealer)


    def tearDown(self):
        self.auction = None


    def stepThroughAuction(self):
        for call in self.calls:
            yield call
            self.auction.makeCall(call)


    def testIsComplete(self):
        """Checking isComplete() only when auction completed"""
        s = self.stepThroughAuction()
        self.assertEqual(self.auction.isComplete(), False)
        try:
            while next(s):
                self.assertEqual(self.auction.isComplete(), False)
        except StopIteration:
            self.assertEqual(self.auction.isComplete(), True)
                

    def testIsPassedOut(self):
        """Checking isPassedOut() when all players pass"""
        for call in [Pass(), Pass(), Pass(), Pass()]:
            self.assertEqual(self.auction.isPassedOut(), False)
            self.auction.makeCall(call)
        self.assertEqual(self.auction.isPassedOut(), True)


    def testCurrentCalls(self):
        """Checking currentBid/currentDouble/currentRedouble values"""
    
        def testCurrent(bid, double, redouble):
            self.assertEqual(self.auction.currentBid, bid)
            self.assertEqual(self.auction.currentDouble, double)
            self.assertEqual(self.auction.currentRedouble, redouble)

        testCurrent(None, None, None)

        bid = Bid(Level.One, Strain.Diamond)
        self.auction.makeCall(bid)
        testCurrent(bid, None, None)  # Ensure that currentBid is set.

        double = Double()
        self.auction.makeCall(double)
        testCurrent(bid, double, None)  # Ensure currentBid/Double set.

        redouble = Redouble()
        self.auction.makeCall(redouble)
        testCurrent(bid, double, redouble)  # Ensure currentBid/Double/Redouble set.

        bid = Bid(Level.One, Strain.Spade)
        self.auction.makeCall(bid)
        testCurrent(bid, None, None)  # Ensure currentBid set, Double/Redouble reset.
        

    def testWhoseTurn(self):
        """Checking whoseTurn() returns position on turn"""
        s = self.stepThroughAuction()
        try:
            turn = self.dealer
            while next(s):
                self.assertEqual(self.auction.whoseTurn(), turn)
                turn = Direction[(turn.index + 1) % 4]  # Turn moves clockwise.
        except StopIteration:
            self.assertEqual(self.auction.whoseTurn(), None)


    def testIsValidCall(self):
        """Checking isValidCall() identifies valid and invalid calls."""
        s = self.stepThroughAuction()
        try:
            while True:
                candidate = next(s)
                self.assertTrue(self.auction.isValidCall(candidate))
                if self.auction.currentBid:
                    pass
                    #self.assert_(self.auction.isValidCall
        except StopIteration:
            pass

