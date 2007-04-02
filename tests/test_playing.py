import unittest
import random

from pybridge.bridge.card import Card
from pybridge.bridge.deck import Deck
from pybridge.bridge.playing import Playing
from pybridge.bridge.symbols import Direction, Rank, Suit


class TestPlaying(unittest.TestCase):

    
    def setUp(self):
        declarer = random.choice(Direction)
        trumps = random.choice(list(Suit) + [None])
        self.deal = Deck().randomDeal()
        self.playing = Playing(declarer, trumps)


    def tearDown(self):
        self.deal = None
        self.playing = None


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


def main():
    suite = unittest.makeSuite(TestPlaying)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()

