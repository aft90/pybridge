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
                    spaces = sum([1 for suitcards in suits.values() if len(suitcards) > 0]) - 1
                    for index, card in enumerate(hand):
                        # Insert a space for each suit in hand which appears before this card's suit.
                        insert = sum([1 for suit, suitcards in suits.items() if len(suitcards) > 0
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
        # Create new ImageSurface for hand.
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)
        # Clear ImageSurface - in Cairo 1.2+, this is done automatically.
        if cairo.version_info < (1, 2):
            context.set_operator(cairo.OPERATOR_CLEAR)
            context.paint()
            context.set_operator(cairo.OPERATOR_OVER)  # Restore.
        
        # Draw cards to surface.
        visible = [(i, card) for i, card in enumerate(hand) if card not in omit]
        for i, card in visible:
            pos_x, pos_y = coords[i][1:]
            self.draw_card(context, pos_x, pos_y, card)
        
        # Save
        self.hands[seat] = {'hand' : hand, 'visible' : visible,
                            'surface' : surface, 'coords' : coords, }
        
        # 
        if seat is self.TOP:
            xy = lambda w, h: ((w - width)/2, self.border_y)
        elif seat is self.RIGHT:
            xy = lambda w, h: ((w - width - self.border_x), (h - height)/2)
        elif seat is self.BOTTOM:
            xy = lambda w, h: ((w - width)/2, (h - height - self.border_y))
        elif seat is self.LEFT:
            xy = lambda w, h: (self.border_x, (h - height)/2)
        
        id = 'hand-%s' % seat  # Identifier for this item.
        if id in self.items:
            self.update_item(id, source=surface, xy=xy)
        else: 
            self.add_item(id, surface, xy, 0)


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
        
        @param trick: a (leader, cards_played) pair.
        """
        width, height = 200, 200
        # (x, y) positions to fit within (width, height) bound box.
        pos = {Seat.North : ((width - self.card_width)/2, 0 ),
               Seat.East  : ((width - self.card_width), (height - self.card_height)/2 ),
               Seat.South : ((width - self.card_width)/2, (height - self.card_height) ),
               Seat.West  : (0, (height - self.card_height)/2 ), }
        
        # Create new ImageSurface for trick.
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)
        # Clear ImageSurface - in Cairo 1.2+, this is done automatically.
        if cairo.version_info < (1, 2):
            context.set_operator(cairo.OPERATOR_CLEAR)
            context.paint()
            context.set_operator(cairo.OPERATOR_OVER)  # Restore.
        
        if trick:
            leader, cards_played = trick
            # The order of play is the leader, then clockwise around Seat.
            for seat in Seat[leader.index:] + Seat[:leader.index]:
                card = cards_played.get(seat)
                if card:
                    pos_x, pos_y = pos[seat]
                    self.draw_card(context, pos_x, pos_y, card)
        
        id = 'trick'
        if id in self.items:
            self.update_item(id, source=surface)
        else: 
            xy = lambda w, h: ((w - width)/2, (h - height)/2)
            self.add_item(id, surface, xy, 0)



    def set_turn(self, seat):
        """
        
        @param seat: a member of Seat.
        """
#        hand_surface = self.hands[seat]['surface']
#        x = self.hands[seat]['xy'] - 10
#        y = self.hands[seat]['xy'] - 10
#        width = surface.get_width() + 20
#        height = surface.get_height() + 20
#        args = ('turn', surface, pos_x, pos_y, -1)
#        if self.items.get('turn'):
#            self.update_item(*args)
#        else:
#            self.add_item(*args)


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

