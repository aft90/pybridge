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

import pybridge.environment as env
from config import config


class CairoCanvas(gtk.DrawingArea):
    """Provides a simple canvas layer for the display of graphics."""

    # TODO: enhance documentation.

    background_path = config['Appearance'].get('Background',
                                               env.find_pixmap('baize.png'))
    background = cairo.ImageSurface.create_from_png(background_path)
    pattern = cairo.SurfacePattern(background)
    pattern.set_extend(cairo.EXTEND_REPEAT)


    def __init__(self):
        super(CairoCanvas, self).__init__()  # Initialise parent.
        
        self.items = {}
        
        # Set up gtk.Widget signals.
        self.connect('configure_event', self.configure)
        self.connect('expose_event', self.expose)


    def clear(self):
        """Clears all items from canvas."""
        self.items = {}  # Remove all item references.
        
        # Redraw background pattern on backing.
        width, height = self.window.get_size()
        context = cairo.Context(self.backing)
        context.rectangle(0, 0, width, height)
        context.set_source(self.pattern)
        context.paint()
        # Trigger a call to self.expose().
        self.window.invalidate_rect((0, 0, width, height), False)


    def add_item(self, id, source, xy, z_index, opacity=1):
        """Places source item into items list.

        @param id: unique identifier for source.
        @param source: ImageSurface.
        @param xy: tuple providing (x, y) coords for source in backing.
        @param z_index: integer.
        @param opacity: integer in range 0 to 1.
        """
        # Calculate and cache the on-screen area of the item.
        area = self.get_area(source, xy)
        self.items[id] = {'source': source, 'area': area, 'xy': xy,
                          'z-index': z_index, 'opacity' : opacity, }
        self.redraw(*area)


    def remove_item(self, id):
        """Removes source item with identifier from items list.

        @param id: unique identifier for source.
        """
        if self.items.get(id):
            area = self.items[id]['area']
            del self.items[id]
            self.redraw(*area)


    def update_item(self, id, source=None, xy=None, z_index=0, opacity=0):
        """
        @param id: unique identifier for source.
        @param source: if specified, ImageSurface.
        @param xy: if specified, tuple providing (x, y) coords for source
                   in backing.
        @param z_index: if specified, integer.
        @param opacity: if specified, integer in range 0 to 1. 
        """
        # If optional parameters are not specified, use stored values.
        z_index = z_index or self.items[id]['z-index']
        opacity = opacity or self.items[id]['opacity']
        if source or xy:
            # If source or xy coords changed, recalculate on-screen area.
            source = source or self.items[id]['source']
            xy = xy or self.items[id]['xy']
            area = self.get_area(source, xy)
            # If area of item has changed, clear item from previous area.
            oldarea = self.items[id]['area']
            if area != oldarea:
                del self.items[id]
                self.redraw(*oldarea)
        else:
            source = self.items[id]['source']
            xy = self.items[id]['xy']
            area = self.items[id]['area']
        
        self.items[id] = {'source': source, 'area': area, 'xy' : xy,
                          'z-index': z_index, 'opacity' : opacity, }
        self.redraw(*area)


    def redraw(self, x, y, width, height):
        """Redraws sources in area (x, y, width, height) to backing canvas.
        
        @param x: start x-coordinate of area to be redrawn.
        @param y: start y-coordinate of area to be redrawn.
        @param width: the width of area to be redrawn.
        @param height: the height of area to be redrawn.
        """
        context = cairo.Context(self.backing)
        context.rectangle(x, y, width, height)
        context.clip()  # Set clip region.

        # Redraw background pattern in area.
        context.set_source(self.pattern)
        context.paint()
        
        # Build list of sources to redraw in area, in order of z-index.
        # TODO: Find sources which intersect with area.
        area = gtk.gdk.Rectangle(x, y, width, height)
        items = self.items.values()
        items.sort(lambda i, j : cmp(i['z-index'], j['z-index']))
        
        for item in items:
            pos_x, pos_y = item['area'][0:2]
            context.set_source_surface(item['source'], pos_x, pos_y)
#            context.paint()
            context.paint_with_alpha(item['opacity'])
        
        context.reset_clip()
        self.window.invalidate_rect((x, y, width, height), False)  # Expose.


    def get_area(self, source, xy):
        """Calculates the on-screen area of the specified source centred at xy.
        
        @param source:
        @param xy:
        @return: a tuple (x, y, width, height)
        """
        win_w, win_h = self.window.get_size()  # Window width and height.
        width, height = source.get_width(), source.get_height()
        x = int((xy[0] * win_w) - width/2)  # Round to integer.
        y = int((xy[1] * win_h) - height/2)
        # Ensure that source coordinates fit inside dimensions of backing.
        if x < self.border_x:
            x = self.border_x
        elif x + width > win_w - self.border_x:
            x = win_w - self.border_x - width
        if y < self.border_y:
            y = self.border_y
        elif y + height > win_h - self.border_y:
            y = win_h - self.border_y - height
        return x, y, width, height


    def new_surface(self, width, height):
        """Creates a new ImageSurface of dimensions (width, height)
        and ensures that the ImageSurface is cleared.
        
        @param width: the expected width of the ImageSurface.
        @param height: the expected height of the ImageSurface.
        @return: tuple (surface, context)
        """
        # Create new ImageSurface for hand.
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)
        # Clear ImageSurface - in Cairo 1.2+, this is done automatically.
        if cairo.version_info < (1, 2):
            context.set_operator(cairo.OPERATOR_CLEAR)
            context.paint()
            context.set_operator(cairo.OPERATOR_OVER)  # Restore.
        return surface, context


    def configure(self, widget, event):
        width, height = self.window.get_size()
        self.backing = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        
        # Recalculate position of all items.
        for id, item in self.items.iteritems():
            self.items[id]['area'] = self.get_area(item['source'], item['xy'])
        
        self.redraw(0, 0, width, height)  # Full redraw required.
        return True  # Expected to return True.


    def expose(self, widget, event):
        context = widget.window.cairo_create()
        context.rectangle(*event.area)
        context.clip()  # Only redraw the exposed area.
        context.set_source_surface(self.backing, 0, 0)
        context.paint()
        context.reset_clip()
        return False  # Expected to return False.

