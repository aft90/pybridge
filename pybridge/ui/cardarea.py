# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2006 PyBridge Project.
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

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import gtk
import cairo
import pango
import pangocairo

from pybridge.environment import environment
from canvas import CairoCanvas

from pybridge.bridge.card import Card, Rank, Suit
from pybridge.bridge.deck import Seat

# The order in which card graphics are expected in card mask.
CARD_MASK_RANKS = [Rank.Ace, Rank.Two, Rank.Three, Rank.Four, Rank.Five,
                   Rank.Six, Rank.Seven, Rank.Eight, Rank.Nine, Rank.Ten,
                   Rank.Jack, Rank.Queen, Rank.King]
CARD_MASK_SUITS = [Suit.Club, Suit.Diamond, Suit.Heart, Suit.Spade]

# The red-black-red-black ordering convention.
RED_BLACK = [Suit.Diamond, Suit.Club, Suit.Heart, Suit.Spade]


class CardArea(CairoCanvas):
    """This widget.

    This widget uses Cairo and requires >= GTK 2.8.
    """

    # Load card mask.
    card_mask_path = environment.find_pixmap('bonded.png')
    card_mask = cairo.ImageSurface.create_from_png(card_mask_path)
    
    font_description = pango.FontDescription('Sans Bold 10')
    
    border_x = border_y = 10
    card_width = card_mask.get_width() / 13
    card_height = card_mask.get_height() / 5
    spacing_x = int(card_width * 0.4)
    spacing_y = int(card_height * 0.2)


    def __init__(self):
        super(CardArea, self).__init__()  # Initialise parent.
        
        # To receive card clicked events, override this with external method.
        self.on_card_clicked = lambda card, seat: True
        
        self.hands = {}
        self.trick = None
        self.set_seat_mapping(Seat.South)
        
        self.connect('button_release_event', self.button_release)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)


    def draw_card(self, context, pos_x, pos_y, card):
        """Draws graphic of specified card to context at (pos_x, pos_y).
        
        @param context: a cairo.Context
        @param pos_x:
        @param pos_y:
        @param card: the Card to draw.
        """
        if isinstance(card, Card):  # Determine coordinates of card graphic.
            src_x = CARD_MASK_RANKS.index(card.rank) * self.card_width
            src_y = CARD_MASK_SUITS.index(card.suit) * self.card_height
        else:  # Draw a face-down card.
            src_x, src_y = self.card_width*2, self.card_height*4
        
        context.rectangle(pos_x, pos_y, self.card_width, self.card_height)
        context.clip()
        context.set_source_surface(self.card_mask, pos_x-src_x, pos_y-src_y)
        context.paint()
        context.reset_clip()


    def set_hand(self, hand, seat, facedown=False, omit=[]):
        """Sets the hand of player at seat.
        Draws representation of cards in hand to context.
        
        The hand is buffered into an ImageSurface, since hands change
        infrequently and multiple calls to draw_card() are expensive.
        
        @param hand: a list of Card objects.
        @param seat: a member of Seat.
        @param facedown: if True, cards are drawn face-down.
        @param omit: a list of elements of hand not to draw.
        """
        
        # TODO: coords should be dict (card : (pos_x, pos_y)), but this breaks when hashing.
        def get_coords_for_hand():
            coords = []
            if seat in (self.TOP, self.BOTTOM):
                pos_y = 0
                if facedown is True:  # Draw cards in one continuous row.
                    for index, card in enumerate(hand):
                        pos_x = index * self.spacing_x
                        coords.append((card, pos_x, pos_y))
                else:  # Insert a space between each suit.
                    spaces = len([1 for suitcards in suits.values() if len(suitcards) > 0]) - 1
                    for index, card in enumerate(hand):
                        # Insert a space for each suit in hand which appears before this card's suit.
                        insert = len([1 for suit, suitcards in suits.items() if len(suitcards) > 0
                                     and RED_BLACK.index(card.suit) > RED_BLACK.index(suit)])
                        pos_x = (index + insert) * self.spacing_x
                        coords.append((card, pos_x, pos_y))
            else:  # LEFT or RIGHT.
                if facedown is True:  # Wrap cards to a 4x4 grid.
                    for index, card in enumerate(hand):
                        adjust = seat is self.RIGHT and index == 12 and 3
                        pos_x = ((index % 4) + adjust) * self.spacing_x
                        pos_y = (index / 4) * self.spacing_y
                        coords.append((card, pos_x, pos_y))
                else:
                    longest = max([len(cards) for cards in suits.values()])
                    for index, card in enumerate(hand):
                        adjust = seat is self.RIGHT and longest - len(suits[card.suit])
                        pos_x = (suits[card.suit].index(card) + adjust) * self.spacing_x
                        pos_y = RED_BLACK.index(card.suit) * self.spacing_y
                        coords.append((card, pos_x, pos_y))
            return coords
        
        if facedown is False:
            # Split hand into suits.
            suits = dict([(suit, []) for suit in Suit])
            for card in hand:
                suits[card.suit].append(card)
            # Sort suits.
            for suit in suits:
                suits[suit].sort(reverse=True)  # High to low.
            # Reorder hand by sorted suits.
            hand = []
            for suit in RED_BLACK:
                hand.extend(suits[suit])
       
        saved = self.hands.get(seat)
        if saved and saved['hand'] == hand:
            # If hand has been set previously, do not recalculate coords.
            coords = saved['coords']
        else:
            coords = get_coords_for_hand()
        
        # Determine dimensions of hand.
        width = max([x for card, x, y in coords]) + self.card_width
        height = max([y for card, x, y in coords]) + self.card_height
        surface, context = self.new_surface(width, height)
        
        # Draw cards to surface.
        visible = [(i, card) for i, card in enumerate(hand) if card not in omit]
        for i, card in visible:
            pos_x, pos_y = coords[i][1:]
            self.draw_card(context, pos_x, pos_y, card)
        
        # Save
        self.hands[seat] = {'hand' : hand, 'visible' : visible,
                            'surface' : surface, 'coords' : coords, }
        
        id = 'hand-%s' % seat  # Identifier for this item.
        if id in self.items:
            self.update_item(id, source=surface)
        else:
            xy = {self.TOP : (0.5, 0.15), self.BOTTOM : (0.5, 0.85),
                  self.LEFT : (0.15, 0.5), self.RIGHT : (0.85, 0.5), }
            self.add_item(id, surface, xy[seat], 0)


    def set_player_name(self, seat, name=None):
        """
        
        @param name: the name of the player, or None.
        """
        id = 'player-%s' % seat
        if name is None or id in self.items:
            self.remove_item(id)
            return
        
        layout = pango.Layout(self.create_pango_context())
        layout.set_font_description(self.font_description)
        layout.set_text(name)
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
            xy = {self.TOP : (0.5, 0.15), self.BOTTOM : (0.5, 0.85),
                  self.LEFT : (0.15, 0.6), self.RIGHT : (0.85, 0.6), }
            self.add_item(id, surface, xy[seat], 2)


    def set_seat_mapping(self, focus=Seat.South):
        """Sets the mapping between seats at table and positions of hands.
        
        @param focus: the Seat to be drawn "closest" to the observer.
        """
        # Assumes Seat elements are ordered clockwise from North.
        order = Seat[focus.index:] + Seat[:focus.index]
        for seat, attr in zip(order, ('BOTTOM', 'LEFT', 'TOP', 'RIGHT')):
            setattr(self, attr, seat)
        # TODO: set seat labels.


    def set_trick(self, trick):
        """Sets the current trick.
        Draws representation of current trick to context.
        
        @param trick: a (leader, cards_played) pair, or None.
        """
        xy = {self.TOP : (0.5, 0.425), self.BOTTOM : (0.5, 0.575),
              self.LEFT : (0.425, 0.5), self.RIGHT : (0.575, 0.5), }
        
        if trick:
            # The order of play is the leader, then clockwise around Seat.
            leader = trick[0]
            order = Seat[leader.index:] + Seat[:leader.index]
            for i, seat in enumerate(order):
                id = 'trick-%s' % seat
                old_card = self.trick and self.trick[1].get(seat) or None
                new_card = trick[1].get(seat)
                # If old card matches new card, take no action.
                if old_card is None and new_card is not None:
                    surface, context = self.new_surface(self.card_width, self.card_height)
                    self.draw_card(context, 0, 0, new_card)
                    self.add_item(id, surface, xy[seat], z_index=i+1)
                elif new_card is None and old_card is not None:
                    self.remove_item(id)
                elif old_card != new_card:
                    surface, context = self.new_surface(self.card_width, self.card_height)
                    self.draw_card(context, 0, 0, new_card)
                    self.update_item(id, surface, z_index=i+1)
        
        elif self.trick:  # Remove all cards from previous trick.
            for seat in self.trick[1]:
                self.remove_item('trick-%s' % seat)
        
        self.trick = trick  # Save trick and return.


    def set_turn(self, turn):
        """Sets the turn indicator.
        
        The turn indicator is displayed as a rounded rectangle around
        the hand matching the specified seat.
        
        @param turn: a member of Seat, or None.
        """
        if turn is None:
            return
        
        for seat in Seat:
            opacity = (seat is turn) and 1 or 0.5
            self.update_item('hand-%s' % seat, opacity=opacity)

#        # TODO: select colours that don't clash with the background.
#        # TODO: one colour if user can play card from hand, another if not.
#        width = self.hands[turn]['surface'].get_width() + 20
#        height = self.hands[turn]['surface'].get_height() + 20
#        surface, context = self.new_surface(width, height)
#        context.set_source_rgb(0.3, 0.6, 0)  # Green.
#        context.paint_with_alpha(0.5)
#        
#        xy = self.items['hand-%s' % turn]['xy']  # Use same xy as hand.
#        
#        if id in self.items:
#            self.update_item(id, source=surface, xy=xy)
#        else:
#            self.add_item(id, surface, xy, -1)


    def button_release(self, widget, event):
        """Determines if a card was clicked: if so, calls card_selected."""
        if event.button == 1:
            found_hand = False
            
            # Determine the hand which was clicked.
            for seat in self.hands:
                card_coords = self.hands[seat]['coords']
                surface = self.hands[seat]['surface']
                hand_x, hand_y = self.items['hand-%s' % seat]['area'][0:2]
                if (hand_x <= event.x <= hand_x + surface.get_width()) and \
                   (hand_y <= event.y <= hand_y + surface.get_height()):
                    found_hand = True
                    break
            
            if found_hand:
                # Determine the card in hand which was clicked.
                pos_x, pos_y = event.x - hand_x, event.y - hand_y
                # Iterate through visible cards backwards.
                for i, card in self.hands[seat]['visible'][::-1]:
                    x, y = card_coords[i][1:]
                    if (x <= pos_x <= x + self.card_width) and \
                       (y <= pos_y <= y + self.card_height):
                        self.on_card_clicked(card, seat)
                        break
        
        return True  # Expected to return True.

