import unittest

from pybridge.bridge.board import Board
from pybridge.bridge.call import Bid, Pass, Double, Redouble
from pybridge.bridge.card import Card
from pybridge.bridge.game import BridgeGame
from pybridge.bridge.symbols import Direction, Level, Strain, Rank, Suit, Vulnerable
from pybridge.network.error import GameError


# A sample board.
#from pybridge.bridge.deck import Deck
#d = Deck()
#hands = d.randomDeal()
hands = dict(zip(Direction, [[Card(r, s) for r in Rank] for s in Suit]))
board = Board(deal=hands, dealer=Direction.North, vuln=Vulnerable.All)


class TestGame(unittest.TestCase):


    def setUp(self):
        self.game = BridgeGame()


    def tearDown(self):
        self.game = None


    def testStart(self):
        """Starting game should reinitialise state"""
        self.assertEqual(self.game.inProgress(), False)
        self.assertRaises(GameError, self.game.getTurn)
        self.game.start()
        self.assertEqual(self.game.inProgress(), True)
        self.assertEqual(self.game.getTurn(), self.game.board['dealer'])


    def testStartWithBoard(self):
        self.game.start(board)
        self.assertEqual(board, self.game.board)
        self.assertEqual(self.game.getTurn(), board['dealer'])


    def testPlayers(self):
        players = {}
        for position in Direction:
            # Associate position with player.
            players[position] = self.game.addPlayer(position)
            # Cannot add another player to the same position.
            self.assertRaises(GameError, self.game.addPlayer, position)
        for position in Direction:
            self.game.removePlayer(position)


    def testGetState(self):
        self.game.start(board)




class TestGameRuns(unittest.TestCase):


    def setUp(self):
        self.game = BridgeGame()
        self.players = {}
        for position in list(Direction):
            self.players[position] = self.game.addPlayer(position)


    def tearDown(self):
        self.game = None
        self.players = {}


    def testBiddingPassedOut(self):
        """All players pass, game should finish without reaching play"""
        self.game.start(board)

        turn = board['dealer']  # Avoid calling getTurn.
        for i in range(len(Direction)):  # Iterate for each player.
            self.players[turn].makeCall( Pass() )  # Each player passes.
            turn = Direction[(turn.index + 1) % len(Direction)]
        self.assertEqual(turn, board['dealer'])  # Sanity check.

        # Bidding is passed out - game is over.
        self.assertEqual(self.game.inProgress(), False)
        # Should not be able to make calls or play cards.
        self.assertRaises(GameError, self.players[turn].makeCall, Bid(Level.One, Strain.Club))
        self.assertRaises(GameError, self.players[turn].playCard, board['deal'][turn][0])


    def testSampleGame(self):
        """Play through a sample game.
        
        This does not attempt to test the integrity of Bidding and Play.
        """
        calls = [Bid(l, s) for l in Level for s in Strain] + [Pass()]*3
        self.game.start(board)

        for call in calls:
            turn = self.game.getTurn()
            self.players[turn].makeCall(call)

        while not self.game.play.isComplete():
            turn = self.game.getTurn()
            # Find a valid card.
            for card in board['deal'][turn]:
                if self.game.play.isValidPlay(card, turn, hand=board['deal'][turn]):
                    if turn == self.game.play.dummy:
                        turn = self.game.play.declarer
                    self.players[turn].playCard(card)
                    break

        self.assertEqual(self.game.inProgress(), False)  # Game complete.
        #self.game.getState()



suite = unittest.TestLoader().loadTestsFromTestCase(TestGame)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(TestGameRuns)
unittest.TextTestRunner(verbosity=2).run(suite)

