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
import cairo
import pango
import pangocairo

import pybridge.environment as env
from canvas import CairoCanvas
from config import config
from vocabulary import *

from pybridge.games.bridge.symbols import Rank, Suit

# The order in which card graphics are expected in card mask.
CARD_MASK_RANKS = [Rank.Ace, Rank.Two, Rank.Three, Rank.Four, Rank.Five,
                   Rank.Six, Rank.Seven, Rank.Eight, Rank.Nine, Rank.Ten,
                   Rank.Jack, Rank.Queen, Rank.King]
CARD_MASK_SUITS = [Suit.Club, Suit.Diamond, Suit.Heart, Suit.Spade]

# The red-black-red-black ordering convention.
RED_BLACK = [Suit.Diamond, Suit.Club, Suit.Heart, Suit.Spade]


class CardArea(CairoCanvas):
    """A graphical display of a 4-player trick-taking card game.
    
    Future considerations:
      - support card games with more/less than 4 players.
    """

    # Load card mask.
    card_mask_file = config['Appearance'].get('CardStyle', 'bonded.png')
    card_mask_path =  env.find_pixmap(card_mask_file)
    card_mask = cairo.ImageSurface.create_from_png(card_mask_path)

    font_description = pango.FontDescription('Sans Bold 10')

    border_x = border_y = 10
    card_width = card_mask.get_width() / 13
    card_height = card_mask.get_height() / 5
    spacing_x = int(card_width * 0.4)
    spacing_y = int(card_height * 0.2)


    def __init__(self, positions):
        """Initialise card area.
        
        To receive card click and hand click signals, please override the
        on_card_clicked and on_hand_clicked methods.
        
        @param positions: a 4-tuple containing position identifiers,
                          starting from top and rotating clockwise.
        """
        super(CardArea, self).__init__()  # Initialise parent.

        self.TOP, self.RIGHT, self.BOTTOM, self.LEFT = positions
        self.focus = self.BOTTOM
        self.hands = {}
        self.trick = None
        self.playernames = {}
        #self.set_player_mapping(Direction.South, redraw=False)

        # Set up gtk.DrawingArea signals.
        self.connect('button_press_event', self._button_press)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)


    def draw_card(self, context, pos_x, pos_y, card):
        """Draws graphic of specified card to context at (pos_x, pos_y).
        
        @param context: a cairo.Context on which to draw the card.
        @param pos_x:
        @param pos_y:
        @param card: the card to draw. Specify a non-card to draw face-down.
        """
        if hasattr(card, 'rank') and hasattr(card, 'suit'):  # A card.
            # Determine coordinates of card graphic within card mask.
            src_x = CARD_MASK_RANKS.index(card.rank) * self.card_width
            src_y = CARD_MASK_SUITS.index(card.suit) * self.card_height
        else:  # Card not specified; draw face-down.
            src_x, src_y = self.card_width*2, self.card_height*4

        context.rectangle(pos_x, pos_y, self.card_width, self.card_height)
        context.clip()
        context.set_source_surface(self.card_mask, pos_x-src_x, pos_y-src_y)
        context.paint()
        context.reset_clip()


    def set_hand(self, hand, position, facedown=False, visible=[]):
        """Sets the hand of player at position. Draws cards in hand to context.
        
        The hand is buffered into an ImageSurface, since hands change
        infrequently and repeated calls to draw_card() are expensive.
        
        @param hand: a list of cards.
        @param position: a member of Direction.
        @param facedown: if True, cards are drawn face-down.
        @param visible: a list of elements of hand to draw.
        """

        def get_coords_for_hand():
            coords = {}
            if position in (self.TOP, self.BOTTOM):
                pos_y = 0
                if facedown is True:  # Draw cards in one continuous row.
                    for index, card in enumerate(hand):
                        pos_x = index * self.spacing_x
                        coords[card] = (pos_x, pos_y)
                else:  # Insert a space between each suit.
                    spaces = len([1 for suitcards in suits.values() if len(suitcards) > 0]) - 1
                    for index, card in enumerate(hand):
                        # Insert a space for each suit in hand which appears before this card's suit.
                        insert = len([1 for suit, suitcards in suits.items() if len(suitcards) > 0
                                     and RED_BLACK.index(card.suit) > RED_BLACK.index(suit)])
                        pos_x = (index + insert) * self.spacing_x
                        coords[card] = (pos_x, pos_y)
            else:  # LEFT or RIGHT.
                if facedown is True:  # Wrap cards to a 4x4 grid.
                    for index, card in enumerate(hand):
                        adjust = position == self.RIGHT and index == 12 and 3
                        pos_x = ((index % 4) + adjust) * self.spacing_x
                        pos_y = (index / 4) * self.spacing_y
                        coords[card] = (pos_x, pos_y)
                else:
                    longest = max([len(cards) for cards in suits.values()])
                    for index, card in enumerate(hand):
                        adjust = position == self.RIGHT and longest - len(suits[card.suit])
                        pos_x = (suits[card.suit].index(card) + adjust) * self.spacing_x
                        pos_y = RED_BLACK.index(card.suit) * self.spacing_y
                        coords[card] = (pos_x, pos_y)
            return coords

        if not facedown:  # Order hand by sorted suits.
            # Split hand into suits.
            suits = dict([(suit, []) for suit in Suit])
            for card in hand:
                suits[card.suit].append(card)
            for suit in suits:
                suits[suit].sort(reverse=True)  # Sort suits, high to low.
            hand = []  # Rebuild hand, ordered by sorted suits.
            for suit in RED_BLACK:
                hand.extend(suits[suit])

        # Retrieve hand information.
        saved = self.hands.get(position)
        if saved and saved['hand'] == hand:
            # Hand has been set previously, so need not recalculate coords.
            coords = saved['coords']
        else:
            coords = get_coords_for_hand()

        # Determine dimensions of hand.
        width = max([x for x, y in coords.values()]) + self.card_width
        height = max([y for x, y in coords.values()]) + self.card_height
        surface, context = self.new_surface(width, height)

        # Draw cards to surface.
        for i, card in enumerate(hand):
            if card in visible:
                pos_x, pos_y = coords[card]
                self.draw_card(context, pos_x, pos_y, card)

        # Save hand information.
        self.hands[position] = {'hand': hand, 'visible': visible,
                    'surface': surface, 'coords': coords, 'facedown': facedown}

        id = ('hand', position)  # Identifier for this item.
        if id in self.items:
            self.update_item(id, source=surface)
        else:
            xy = {self.TOP: (0.5, 0.15), self.BOTTOM: (0.5, 0.85),
                  self.LEFT: (0.15, 0.5), self.RIGHT: (0.85, 0.5)}
            opacity = (self.playernames.get(position) is None) and 0.5 or 1
            self.add_item(id, surface, xy[position], 0, opacity=opacity)


    def set_player_name(self, position, name=None):
        """Sets the name of the player at position.
        
        @param position: the position of the player.
        @param name: the name of the player, or None for no player.
        """
        self.playernames[position] = name
        id = ('playername', position)  # Identifier for player name item.

        # If no name specified, show hand at position as translucent.
        handid = ('hand', position)
        if handid in self.items:
            opacity = (name and 1) or 0.5
            self.update_item(handid, opacity=opacity)

        layout = pango.Layout(self.create_pango_context())
        layout.set_font_description(self.font_description)
        if name is None:
            layout.set_text(DIRECTION_NAMES[position])
        else:
            layout.set_text(DIRECTION_NAMES[position] + ': ' + name)

        # Create an ImageSurface respective to dimensions of text.
        width, height = layout.get_pixel_size()
        width += 8; height += 4
        surface, context = self.new_surface(width, height)
        context = pangocairo.CairoContext(context)

        # Draw background box, text to ImageSurface.
        context.set_line_width(4)
        context.rectangle(0, 0, width, height)
        context.set_source_rgb(0, 0.5, 0)
        context.fill_preserve()
        context.set_source_rgb(0, 0.25, 0)
        context.stroke()
        context.move_to(4, 2)
        context.set_source_rgb(1, 1, 1)
        context.show_layout(layout)

        if id in self.items:
            self.update_item(id, source=surface)
        else:
            xy = {self.TOP : (0.5, 0.2), self.BOTTOM : (0.5, 0.9),
                  self.LEFT : (0.125, 0.625), self.RIGHT : (0.875, 0.625), }
            self.add_item(id, surface, xy[position], 2)


    def set_player_mapping(self, focus=Direction.South, redraw=True):
        """Sets the mapping between players at table and positions of hands.
        
        @param focus: the position to be drawn "closest" to the observer.
        @param redraw: if True, redraw the card area display immediately.
        """
        # Assumes Direction elements are ordered clockwise from North.
        order = Direction[focus.index:] + Direction[:focus.index]
        for player, attr in zip(order, ('BOTTOM', 'LEFT', 'TOP', 'RIGHT')):
            setattr(self, attr, player)

        # Only redraw if focus has changed.
        if redraw and focus != self.focus:
            self.focus = focus
            self.clear()  # Wipe all saved ImageSurface objects - not subtle!

            # Use a copy of self.hands, since it will be changed by set_hand().
            hands = self.hands.copy()
            self.hands.clear()
            for position in Direction:
                self.set_player_name(position, self.playernames.get(position))
                self.set_hand(hands[position]['hand'], position,
                              facedown=hands[position]['facedown'],
                              visible=hands[position]['visible'])

            trick = self.trick
            self.trick = None
            self.set_trick(trick)

        
    def set_trick(self, trick):
        """Sets the current trick.
        Draws representation of current trick to context.
        
        @param trick: a (leader, cards_played) pair, or None.
        """
        xy = {self.TOP : (0.5, 0.425), self.BOTTOM : (0.5, 0.575),
              self.LEFT : (0.425, 0.5), self.RIGHT : (0.575, 0.5), }

        if trick:
            leader, cards = trick
            # The order of play is the leader, then clockwise around Direction.
            order = Direction[leader.index:] + Direction[:leader.index]
            for i, position in enumerate(order):
                id = ('trick', position)
                old_card = self.trick and self.trick[1].get(position) or None
                new_card = cards.get(position) or None

                # If old card matches new card, take no action.
                if old_card is None and new_card is not None:
                    surface, context = self.new_surface(self.card_width, self.card_height)
                    self.draw_card(context, 0, 0, new_card)
                    self.add_item(id, surface, xy[position], z_index=i+1)
                elif new_card is None and old_card is not None:
                    self.remove_item(id)
                elif old_card != new_card:
                    surface, context = self.new_surface(self.card_width, self.card_height)
                    self.draw_card(context, 0, 0, new_card)
                    self.update_item(id, surface, z_index=i+1)

        elif self.trick:  # Remove all cards from previous trick.
            for position in self.trick[1]:
                id = ('trick', position)
                if id in self.items:
                    self.remove_item(id)

        self.trick = trick  # Save trick.


    def on_card_clicked(self, card, position):
        """Called when a card is clicked by user.
        
        @param card: the card clicked.
        @param position: the position of hand which contains card.
        """
        pass  # Override this method.


    def on_hand_clicked(self, position):
        """Called when a hand is clicked by user.
        
        @param position: the position of hand.
        """
        pass  # Override this method.


    def _button_press(self, widget, event):
        """Determines if a card was clicked: if so, calls on_card_selected."""
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            found_hand = False
    
            # Determine the hand which was clicked.
            for position in self.hands:
                card_coords = self.hands[position]['coords']
                surface = self.hands[position]['surface']
                hand_x, hand_y = self.items[('hand', position)]['area'][0:2]
                if (hand_x <= event.x <= hand_x + surface.get_width()) and \
                   (hand_y <= event.y <= hand_y + surface.get_height()):
                    found_hand = True
                    break

            if found_hand:
                self.on_hand_clicked(position)

                # Determine the card in hand which was clicked.
                pos_x, pos_y = event.x - hand_x, event.y - hand_y
                # Iterate through visible cards backwards.
                for card in reversed(self.hands[position]['hand']):
                    if card in self.hands[position]['visible']:
                        x, y = card_coords[card]
                        if (x <= pos_x <= x + self.card_width) and \
                           (y <= pos_y <= y + self.card_height):
                            self.on_card_clicked(card, position)
                            break

        return True  # Expected to return True.

