import unittest

from pybridge.games.bridge.card import Card
from pybridge.games.bridge.deal import Deal
from pybridge.games.bridge.symbols import Direction, Rank, Suit


class TestDeck(unittest.TestCase):

    cards = sorted(Card(r, s) for r in Rank for s in Suit)

    samples = {}

    samples[1] = Deal({Direction.North: [Card(r, Suit.Spade) for r in Rank],
                       Direction.East:  [Card(r, Suit.Heart) for r in Rank],
                       Direction.South: [Card(r, Suit.Diamond) for r in Rank],
                       Direction.West:  [Card(r, Suit.Club) for r in Rank]})

    # http://bridgehands.com/D/Duke_of_Cumberland_Hand.htm
    samples[25216995119420903953708290155] = Deal.fromString(
        "N:..Q8765432.AQT84 65432.T9872.JT9. T987.6543..76532 AKQJ.AKQJ.AK.KJ9")

    # http://bridgehands.com/B/John_Bennett_Murder.htm
    samples[49115408832893597588305377049] = Deal.fromString(
        "S:KJ985.K762.85.KT Q72.AJ3.AQT92.J6 AT63.T85.4.A9842 4.Q94.KJ763.Q753")

    # From the PBN v2.0 specification document.
    samples[51845212465382378289082480212] = Deal.fromString(
        "N:.63.AKQ987.A9732 A8654.KQ5.T.QJT6 J973.J98742.3.K4 KQT2.AT.J6542.85")

    # http://bridgehands.com/M/Mississippi_Heart_Hand.htm
    samples[53520933857671775260919265981] = Deal.fromString(
        "S:AKQ.AKQJT9..AKQJ .8765432.AKQJT9. T5432..5432.5432 J9876..876.T9876")


    def validateDeal(self, deal):
        """Checks that structure of deal conforms to requirements:
        
        - Each position in Direction maps to a hand, represented as a list.
        - Hand lists contain exactly 13 Card objects.
        - No card may be repeated in the same hand, or between hands.
        
        @param deal: a Deal instance.
        """
        assert isinstance(deal, Deal), "deal not a Deal instance"
        assert set(deal.keys()) == set(Direction), "invalid set of keys"

        extractcards = []
        for pos, hand in deal.items():
            assert len(hand) == 13, "%s hand does not contain 13 cards" % pos
            extractcards.extend(hand)
        assert self.cards == sorted(extractcards), "not a pure set of cards"


    def test_generateRandom(self):
        """Testing generation of random deals"""
        deal = Deal.fromRandom()
        try:
            self.validateDeal(deal)
        except Exception, e:
            self.fail(e, deal)


    def test_toIndex(self):
        """Testing toIndex method over a set of known deals"""
        for index, deal in self.samples.items():
            self.assertEqual(deal.toIndex(), index)


    def test_fromIndex(self):
        """Testing Deal.fromIndex over a set of known indexes"""
        for index, deal in self.samples.items():
            self.assertEqual(Deal.fromIndex(index), deal)


def main():
    suite = unittest.makeSuite(TestDeck)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()

