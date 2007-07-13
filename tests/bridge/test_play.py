import unittest

from pybridge.games.bridge.card import Card
from pybridge.games.bridge.deck import Deck
from pybridge.games.bridge.play import TrickPlay
from pybridge.games.bridge.symbols import Direction, Rank, Suit


class TestTrickPlay(unittest.TestCase):

    deal = Deck().indexToDeal(31415926535897932384626433832)  # Pi!
    declarer = Direction.North
    trumpSuit = Suit.Spade


    def setUp(self):
        self.trickplay = TrickPlay(self.declarer, self.trumpSuit)


    def tearDown(self):
        self.trickplay = None


    def stepThroughTrickPlay(self):
        for i in range(52):
            card, position = self.getValidArgsForPlayCard()
            yield card, position
            self.trickplay.playCard(card, position)


    def getValidArgsForPlayCard(self):
        # Select the next card to play, deterministically.
        assert not self.trickplay.isComplete()
        turn = self.trickplay.whoseTurn()
        card = self.deal[turn][0]
        # Assumes correctness of isValidCardPlay.
        while not self.trickplay.isValidCardPlay(card, self.deal):
            card = self.deal[turn][self.deal[turn].index(card) + 1]
        return card, turn


    def testIsComplete(self):
        s = self.stepThroughTrickPlay()
        try:
            while s.next():
                self.assertEqual(self.trickplay.isComplete(), False)
        except StopIteration:
            self.assertEqual(self.trickplay.isComplete(), True)
#        for trick in self.trickplay:
#            print "leader", trick.leader
#            for pos, card in trick.items():
#                print str(pos), card 
#            print "winner", trick.winner, trick.winningCard


    def testWhoseTurn(self):
        s = self.stepThroughTrickPlay()
        self.assertEqual(self.trickplay.whoseTurn(), self.trickplay.lho)

'''
    def testWhoseTurn(self):
        """whoseTurn"""
        while not self.playing.isComplete():
            # Determine whose turn it should be.
            trick = self.playing.getCurrentTrick()
            leader, cards = trick
            if len(cards) == 4:
                turn = self.playing.whoPlayed(self.playing.winningCard(trick))
            else:
                turn = Direction[(leader.index + len(cards)) % 4]

            # Check that whoseTurn() works.
            self.assertEqual(self.playing.whoseTurn(), turn)
            
            # Play a card for the next iteration.
            hand = self.deal[turn]
            for card in hand:
                if self.playing.isValidPlay(card, turn, hand):
                    break
            self.playing.playCard(card, turn, hand)
'''


def main():
    suite = unittest.makeSuite(TestTrickPlay)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()

