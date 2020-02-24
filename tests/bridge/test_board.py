import unittest

from pybridge.games.bridge.board import Board
from pybridge.games.bridge.symbols import Direction, Vulnerable


class TestCard(unittest.TestCase):

    def testInitialisation(self):
        fb = Board.first()
        self.assertEqual(1, fb['num'])
        self.assertEqual(Direction.North, fb['dealer'])
        self.assertEqual(Vulnerable.Nil, fb['vuln'])

    def testIteration(self):
        fb = Board.first()

        fb = next(fb)
        self.assertEqual(2, fb['num'])
        self.assertEqual(Direction.East, fb['dealer'])
        self.assertEqual(Vulnerable.NorthSouth, fb['vuln'])


        fb = next(fb)
        self.assertEqual(3, fb['num'])
        self.assertEqual(Direction.South, fb['dealer'])
        self.assertEqual(Vulnerable.EastWest, fb['vuln'])

        fb = next(fb)
        self.assertEqual(4, fb['num'])
        self.assertEqual(Direction.West, fb['dealer'])
        self.assertEqual(Vulnerable.All, fb['vuln'])




