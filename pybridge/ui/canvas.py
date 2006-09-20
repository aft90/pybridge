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


class CairoCanvas(gtk.DrawingArea):
    """Provides a simple canvas layer for .
    
    Overlapping items.
    """

    background_path = environment.find_pixmap('baize.png')
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
        self.window.invalidate_rect((0, 0, width, height), False)  # Expose.


    def add_item(self, id, source, xy, z_index):
        """Places source item into items list.

        @param id: unique identifier for source.
        @param source: ImageSurface.
        @param xy: function providing (x, y) coords for source in backing.
        @param z_index: integer.
        """
        pos_x, pos_y = xy(*self.window.get_size())
        area = (pos_x, pos_y, source.get_width(), source.get_height())
        self.items[id] = {'source': source, 'area': area,
                          'xy' : xy, 'z-index': z_index, }
        self.redraw(*area)


    def remove_item(self, id):
        """Removes source item with identifier from items list.

        @param id: unique identifier for source.
        """
        if self.items.get(id):
            area = self.items[id]['area']
            del self.item[id]
            self.redraw(*area)


    def update_item(self, id, source=None, xy=None, z_index=0):
        """
        
        """
        # If optional parameters are not specified, use previous values.
        source = source or self.items[id]['source']
        xy = xy or self.items[id]['xy']
        z_index = z_index or self.items[id]['z-index']
        
        oldarea = self.items[id]['area']  # Current position of item.
        pos_x, pos_y = xy(*self.window.get_size())
        area = (pos_x, pos_y, source.get_width(), source.get_height())
        if area != oldarea:  # If position has changed, clear previous area.
            del self.items[id]
            self.redraw(*oldarea)
        self.items[id] = {'source': source, 'area': area,
                          'xy' : xy, 'z-index': z_index, }
        self.redraw(*area)


    def redraw(self, x, y, width, height):
        """Redraws sources in area (x, y, width, height) to backing canvas.
        
        @param x:
        @param y:
        @param width:
        @param height:
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
        items.sort(lambda i, j : cmp(i['z-index'], j['z-index']), reverse=True)
        
        for item in items:
            pos_x, pos_y = item['area'][0:2]
            context.set_source_surface(item['source'], pos_x, pos_y)
            context.paint()
        
        context.reset_clip()
        self.window.invalidate_rect((x, y, width, height), False)  # Expose.



    def configure(self, widget, event):
        width, height = self.window.get_size()
        self.backing = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        
        # Recalculate position of all items.
        for id, item in self.items.items():
            pos_x, pos_y = item['xy'](width, height)
            area = (pos_x, pos_y, item['area'][2], item['area'][3])
            self.items[id]['area'] = area
        
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

