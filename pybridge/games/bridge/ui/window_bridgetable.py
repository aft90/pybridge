# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2007 PyBridge Project.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import gtk

from pybridge.network.client import client
from pybridge.network.error import GameError

from pybridge.ui.cardarea import CardArea
from pybridge.ui.config import config
from pybridge.ui.eventhandler import SimpleEventHandler
from pybridge.ui.manager import WindowManager
from pybridge.ui.vocabulary import *

from pybridge.ui.window_gametable import WindowGameTable
from window_bidbox import WindowBidbox


class BiddingView(gtk.TreeView):
    """A view of all calls made in an auction."""


    def __init__(self):
        gtk.TreeView.__init__(self)
        self.set_rules_hint(True)

        self.store = gtk.ListStore(str, str, str, str)
        self.set_model(self.store)
        self.clear = self.store.clear
        renderer = gtk.CellRendererText()
        renderer.set_property('size-points', 12)
        renderer.set_property('xalign', 0.5)

        # Set up columns, each corresponding to a position.
        for index, position in enumerate(Direction):
            title = DIRECTION_NAMES[position]
            column = gtk.TreeViewColumn(title, renderer, markup=index)
            self.append_column(column)


    def add_call(self, call, position):
        """Adds call from specified position."""
        column = position.index
        if column == 0 or self.store.get_iter_first() == None:
            iter = self.store.append()
        else:  # Get bottom row. There must be a better way than this...
            iter = self.store.get_iter_first()
            while self.store.iter_next(iter) != None:
                iter = self.store.iter_next(iter)

        format = render_call(call)
        self.store.set(iter, column, format)




class TrickArea(CardArea):
    """A display of the previous trick."""

    # TODO: consider providing support for user to review all previous tricks.
    # However, this may break the Laws of Bridge, and also slow down play.

    border_x, border_y = 6, 6

    trick_xy = property(lambda s: {s.TOP: (0.5, 0.2), s.BOTTOM: (0.5, 0.8),
                                   s.LEFT: (0.2, 0.5), s.RIGHT: (0.8, 0.5)})




class ScoreView(gtk.TreeView):
    """A display of contracts bid, their results and their scores."""


    def __init__(self):
        gtk.TreeView.__init__(self)
        self.set_rules_hint(True)

        self.store = gtk.ListStore(str, str, str, str)
        self.set_model(self.store)
        self.clear = self.store.clear
        renderer = gtk.CellRendererText()

        for index, title in enumerate([_('Contract'), _('Made'), _('N/S'), _('E/W')]):
            column = gtk.TreeViewColumn(title, renderer, markup=index)
            self.append_column(column)


    def add_score(self, game):
        declarerWon, defenceWon = game.play.wonTrickCount()
        score = game.getScore()

        textContract = render_contract(game.contract)
        textMade = str(declarerWon)
        if game.contract.declarer in (Direction.North, Direction.South) and score > 0 \
        or game.contract.declarer in (Direction.East, Direction.West) and score < 0:
            textNS, textEW = str(abs(score)), ''
        else:
            textNS, textEW = '', str(abs(score))

        self.store.prepend([textContract, textMade, textNS, textEW]) 




class BridgeDashboard(gtk.VBox): 
    """An at-a-glance display of the state of a bridge game."""


    def __init__(self):
        gtk.VBox.__init__(self)
        self.set_spacing(4)

        self.contract = gtk.Label()
        self.pack_start(self.contract)

        hbox = gtk.HBox()
        hbox.set_homogeneous(True)
        hbox.set_spacing(6)
        self.declarer_tricks = gtk.Label()
        frame = gtk.Frame()
        frame.set_label(_('Declarer'))
        frame.set_label_align(0.5, 0.5)
        frame.add(self.declarer_tricks)
        hbox.pack_start(frame)
        self.defence_tricks = gtk.Label()
        frame = gtk.Frame()
        frame.set_label(_('Defence'))
        frame.set_label_align(0.5, 0.5)
        frame.add(self.defence_tricks)
        hbox.pack_start(frame)
        self.pack_start(hbox)

        hbox = gtk.HBox()
        hbox.set_homogeneous(True)
        hbox.set_spacing(6)
        # TODO: display board number?
        self.dealer = gtk.Label()
        self.dealer.set_alignment(0, 0.5)
        hbox.pack_start(self.dealer)
        self.vulnerability = gtk.Label()
        self.vulnerability.set_alignment(0, 0.5)
        hbox.pack_start(self.vulnerability)
        self.pack_start(hbox)


    def set_contract(self, game):
        if game.contract:
            text = render_contract(game.contract)
        else:
            text = _('No contract')
        self.contract.set_markup("<span size='x-large'>%s</span>" % text)


    def set_trickcount(self, game):
        if game.play:
            declarerWon, defenceWon = game.play.wonTrickCount()
            required = game.contract.bid.level.index + 7
            declarerNeeds = max(0, required - declarerWon)
            defenceNeeds = max(0, 13 + 1 - required - defenceWon)
        else:
            declarerWon, defenceWon, declarerNeeds, defenceNeeds = 0, 0, 0, 0
        format = "<span size='x-large'><b>%s</b> (%s)</span>"
        self.declarer_tricks.set_markup(format % (declarerWon, declarerNeeds))
        self.defence_tricks.set_markup(format % (defenceWon, defenceNeeds))


    def set_dealer(self, game):
        if game.inProgress():
            dealertext = "<b>%s</b>" % DIRECTION_NAMES[game.board['dealer']]
        else:
            dealertext = ''
        self.dealer.set_markup(_('Dealer') + ': ' + dealertext)


    def set_vulnerability(self, game):
        if game.inProgress():
            vulntext = "<b>%s</b>" % VULN_SYMBOLS[game.board['vuln']]
        else:
            vulntext = ''
        self.vulnerability.set_markup(_('Vuln') + ': ' + vulntext)




class WindowBridgeTable(WindowGameTable):

    gametype = _('Contract Bridge')

    stockdirections = [gtk.STOCK_GO_UP, gtk.STOCK_GO_FORWARD,
                       gtk.STOCK_GO_DOWN, gtk.STOCK_GO_BACK]


    def setUp(self):
        super(WindowBridgeTable, self).setUp()

        # Set up menu attached to 'Take Seat' toolbar button.
        self.takeseat_menuitems = {}
        menu = gtk.Menu()
        for position, stock in zip(Direction, self.stockdirections):
            item = gtk.ImageMenuItem(DIRECTION_NAMES[position], True)
            item.set_image(gtk.image_new_from_stock(stock, gtk.ICON_SIZE_MENU))
            item.connect('activate', self.on_takeseat_clicked, position)
            item.show()
            menu.append(item)
            self.takeseat_menuitems[position] = item
        self.takeseat.set_menu(menu)

        # Set up CardArea widget.
        self.cardarea = CardArea(positions=Direction)

        self.cardarea.on_card_clicked = self.on_card_clicked
        self.cardarea.on_hand_clicked = self.on_hand_clicked
        self.cardarea.set_size_request(640, 480)
        self.gamearea.add(self.cardarea)

        # Set up sidebar.
        self.dashboard = BridgeDashboard()
        self.sidebar.pack_start(self.dashboard, expand=False)

        self.biddingview = BiddingView()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sw.add(self.biddingview)
        frame = gtk.Frame()
        frame.add(sw)
        exp = gtk.Expander(_('Bidding'))
        exp.set_expanded(True)
        exp.add(frame)
        self.sidebar.pack_start(exp)

        self.trickarea = TrickArea(positions=Direction)
        self.trickarea.set_size_request(-1, 180)
        frame = gtk.Frame()
        frame.add(self.trickarea)
        exp = gtk.Expander(_('Previous Trick'))
        exp.set_expanded(True)
        exp.add(frame)
        self.sidebar.pack_start(exp, expand=False)

        self.scoreview = ScoreView()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.scoreview)
        frame = gtk.Frame()
        frame.add(sw)
        exp = gtk.Expander(_('Score Sheet'))
        exp.set_expanded(False)
        exp.add(frame)
        self.sidebar.pack_start(exp, expand=False)


    def errback(self, failure):
        print "Error: %s" % failure.getErrorMessage()
        print failure.getBriefTraceback()


    def setTable(self, table):
        """Changes display to match the table specified.
        
        @param table: the (now) focal table.
        """
        super(WindowBridgeTable, self).setTable(table)

        self.table.game.attach(self.eventHandler)
        self.resetGame()

        for position in Direction:
            self.redrawHand(position)  # Redraw all hands.

        if self.table.game.inProgress():
            # If trick play in progress, redraw trick.
            if self.table.game.play is not None:
                self.redrawTrick()
                if len(self.table.game.play) > 1:
                    self.trickarea.set_trick(self.table.game.play[-2])

            self.setTurnIndicator()

            for call in self.table.game.auction:
                position = self.table.game.auction.whoCalled(call)
                self.biddingview.add_call(call, position)

            # If user is a player and auction in progress, open bidding box.
            if self.player and not self.table.game.auction.isComplete():
                bidbox = self.children.open(WindowBidbox, parent=self)
                bidbox.setCallSelectHandler(self.on_call_selected)
                bidbox.setTable(self.table, self.position)


        # Initialise seat menu and player labels.
        for position in Direction:
            player = self.table.players.get(position)  # Player name or None.

            avail = player is None or position == self.position
            self.takeseat_menuitems[position].set_property('sensitive', avail)
            # If player == None, this unsets player name.
            self.cardarea.set_player_name(position, player)


    def resetGame(self):
        """Clear bidding history, contract, trick counts."""
        self.cardarea.clear()
        self.biddingview.clear()   # Reset bidding history.
        self.trickarea.set_trick(None)

        self.dashboard.set_contract(self.table.game)
        self.dashboard.set_trickcount(self.table.game)
        self.dashboard.set_dealer(self.table.game)
        self.dashboard.set_vulnerability(self.table.game)


    def gameComplete(self):
        # Display all previously revealed hands - the server will reveal the others.
        for position in self.table.game.visibleHands:
            self.redrawHand(position, all=True)

        self.setTurnIndicator()

        dialog = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_INFO)
        dialog.set_title(_('Game result'))

        # Determine and display score in dialog box and score sheet.
        if self.table.game.contract:
            self.scoreview.add_score(self.table.game)

            declarerWon, defenceWon = self.table.game.play.wonTrickCount()
            required = self.table.game.contract.bid.level.index + 7
            offset = declarerWon - required
            score = self.table.game.getScore()

            fields = {'contract': render_contract(self.table.game.contract),
                      'offset': abs(offset) }
            if offset > 0:
                if offset == 1:
                    resultText = _('Contract %(contract)s made by 1 trick.') % fields
                else:
                    resultText = _('Contract %(contract)s made by %(offset)s tricks.') % fields
            elif offset < 0:
                if offset == -1:
                    resultText = _('Contract %(contract)s failed by 1 trick.') % fields
                else:
                    resultText = _('Contract %(contract)s failed by %(offset)s tricks.') % fields
            else:
                resultText = _('Contract %(contract)s made exactly.') % fields

            pair = (score >= 0 and _('declarer')) or _('defence')
            scoreText = _('Score %(points)s points for %(pair)s.') % {'points': abs(score), 'pair': pair}

            dialog.set_markup(resultText + '\n' + scoreText)

        else:
            dialog.set_markup(_('Bidding passed out.'))
            dialog.format_secondary_text(_('No score.'))

        if self.player:
            dialog.add_button(_('Leave Seat'), gtk.RESPONSE_CANCEL)
            dialog.format_secondary_text(_('Click OK to start next game.'))
        dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        dialog.set_default_response(gtk.RESPONSE_OK)
        # If user leaves table (ie. closes window), close dialog as well.
        dialog.set_transient_for(self.window)
        dialog.set_destroy_with_parent(True)

        def dialog_response_cb(dialog, response_id):
            dialog.destroy()
            if self.player:
                if response_id == gtk.RESPONSE_OK and self.table.game.isNextGameReady():
                    d = self.player.callRemote('startNextGame')
                    d.addErrback(self.errback)
                elif response_id == gtk.RESPONSE_CANCEL:
                    self.on_leaveseat_clicked(dialog)

        dialog.connect('response', dialog_response_cb)
        dialog.show()


    def redrawHand(self, position, all=False):
        """Redraws cards making up the hand at position.
        
        Cards played are filtered out and omitted from display.
        Unknown cards are displayed face down.
        
        @param position:
        @param all: If True, do not filter out cards played.
        """
        try:
            hand = self.table.game.getHand(position)
            facedown = False
        except GameError:  # Unknown hand.
            hand = range(13)
            facedown = True

        if all is True or self.table.game.play is None:
            available = hand
        else:
            played = [trick[position] for trick in self.table.game.play if trick.get(position)]
            if facedown:  # Draw cards face down for unknown hand. 
                available = range(13 - len(played))
            else:
                available = [card for card in hand if card not in played]

        self.cardarea.set_hand(hand, position, facedown, visible=available)


    def redrawTrick(self):
        """Redraws trick.
        
        @param table:
        @param trick:
        """
        trick = None
        if self.table.game.play:
            trick = self.table.game.play[-1]
        self.cardarea.set_trick(trick)


    def setTurnIndicator(self):
        """Sets the statusbar text to indicate which player is on turn."""
        context = self.statusbar.get_context_id('turn')
        self.statusbar.pop(context)

        try:
            turn = self.table.game.getTurn()

            if self.table.game.play is not None:
                declarer, dummy = self.table.game.play.declarer, self.table.game.play.dummy
                if self.position and self.position == turn != dummy:
                    text = _("Play a card from your hand.")
                elif self.position and self.position == declarer and turn == dummy:
                    text = _("Play a card from dummy's hand.")
                else:
                    text = _("It is %s's turn to play a card.") % DIRECTION_NAMES[turn]

            else:  # Bidding.
                if self.position and self.position == turn:
                    text = _("Make a call from the bidding box.")
                else:
                    text = _("It is %s's turn to make a call.") % DIRECTION_NAMES[turn]

        except GameError:  # Game not in progress.
            text = _("Waiting for next game to start.")

        self.statusbar.push(context, text)


# Registered event handlers.


    def event_joinGame(self, player, position):
        self.cardarea.set_player_name(position, player)
        # Disable menu item corresponding to position.
        widget = self.takeseat_menuitems[position]
        widget.set_property('sensitive', False)

        # If all positions occupied, disable Take Seat.
        if len(self.table.players.values()) == len(Direction):
            self.takeseat.set_property('sensitive', False)

        if self.player and self.table.game.isNextGameReady():
            d = self.player.callRemote('startNextGame')
            d.addErrback(self.errback)


    def event_leaveGame(self, player, position):
        self.cardarea.set_player_name(position, None)
        # Enable menu item corresponding to position.
        widget = self.takeseat_menuitems[position]
        widget.set_property('sensitive', True)

        # If we are not seated, ensure Take Seat is enabled.
        if self.position is None:
            self.takeseat.set_property('sensitive', True)


    def event_start(self, board):
        self.resetGame()

        # Re-initialise player labels.
        # TODO: shouldn't need to do this.
        for position in Direction:
            player = self.table.players.get(position)  # Player name or None.
            self.cardarea.set_player_name(position, player)

        self.redrawTrick()  # Clear trick.
        for position in Direction:
            self.redrawHand(position)

        self.setTurnIndicator()
        self.dashboard.set_dealer(self.table.game)
        self.dashboard.set_vulnerability(self.table.game)

        if self.player:
            d = self.player.callRemote('getHand')
            # When user's hand is returned, reveal it to client-side Game.
            d.addCallbacks(self.table.game.revealHand, self.errback,
                           callbackKeywords={'position': self.position})
            bidbox = self.children.open(WindowBidbox, parent=self)
            bidbox.setCallSelectHandler(self.on_call_selected)
            bidbox.setTable(self.table, self.position)


    def event_makeCall(self, call, position):
        self.biddingview.add_call(call, position)
        self.setTurnIndicator()

        if self.table.game.auction.isComplete():
            self.dashboard.set_contract(self.table.game)
            if self.children.get(WindowBidbox):  # If a player.
                self.children.close(self.children[WindowBidbox])

        if not self.table.game.inProgress():
            self.gameComplete()


    def event_playCard(self, card, position):
        # Determine the position of the hand from which card was played.
        playfrom = self.table.game.play[-1].whoPlayed(card)
        self.setTurnIndicator()
        self.dashboard.set_trickcount(self.table.game)
        self.redrawTrick()
        self.redrawHand(playfrom)
        if len(self.table.game.play) > 1:
            self.trickarea.set_trick(self.table.game.play[-2])

        if not self.table.game.inProgress():
            self.gameComplete()


    def event_revealHand(self, hand, position):
        all = not self.table.game.inProgress()
        self.redrawHand(position, all)  # Show all cards if game has finished.


# Signal handlers.


    def on_call_selected(self, call):
        if self.player:
            d = self.player.callRemote('makeCall', call)
            d.addErrback(self.errback)


    def on_hand_clicked(self, position):
        if not self.player and not self.table.players.get(position):
            # Join game at position.
            self.on_takeseat_clicked(self.cardarea, position)


    def on_card_clicked(self, card, position):
        if self.player:
            if self.table.game.inProgress() and self.table.game.play is not None:
                d = self.player.callRemote('playCard', card)
                d.addErrback(self.errback)


    def on_takeseat_clicked(self, widget, position=None):

        def success(r):
            self.cardarea.set_position_mapping(self.position)
            self.trickarea.set_position_mapping(self.position)
            if self.table.game.inProgress():
                d = self.player.callRemote('getHand')
                d.addCallbacks(self.table.game.revealHand, self.errback,
                               callbackKeywords={'position' : self.position})
                # If game is running and auction is active, open bidding box.
                if not self.table.game.auction.isComplete():
                    bidbox = self.children.open(WindowBidbox, parent=self)
                    bidbox.setCallSelectHandler(self.on_call_selected)
                    bidbox.setTable(self.table, self.position)

        # TODO: match user up with preferred partner.
        if position is None:
            # No position specified by user: choose an arbitary position.
            position = [p for p in Direction if p not in self.table.players][0]
        d = super(WindowBridgeTable, self).on_takeseat_clicked(widget, position)
        d.addCallback(success)


    def on_leaveseat_clicked(self, widget, *args):

        def success(r):
            if self.children.get(WindowBidbox):
                self.children.close(self.children[WindowBidbox])

        d = super(WindowBridgeTable, self).on_leaveseat_clicked(widget, *args)
        d.addCallback(success)

