import collections
import math

from gi.repository import Gtk, Gdk, Rsvg
import kdtree
import cairo

class Pin:
    """
        A class to be used with the KDtree. For the KD tree the object needs
        to be accessible by indices.

        We also operate in 2D, so that's why it returns 2 for __len__.
    """

    def __init__(self, x=0.0, y=0.0, node=''):
        self.x = x
        self.y = y
        self.node = node

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index out of bounds")

    def __len__(self):
        return 2

class PCBWidget(Gtk.DrawingArea):
    def __init__(self, svg_file, *args, **kwargs):
        Gtk.DrawingArea.__init__(self, *args, **kwargs)

        self.surface = None
        self.svg_handle = Rsvg.Handle.new_from_file(svg_file)
        self.points_to_highlight = []

        self.pins = kdtree.create(dimensions=2)

        self.connect('draw', self.on_draw)
        self.connect('configure-event', self.on_configure)

        # Mouse events
        self.connect('motion-notify-event', self.on_motion_notify)
        self.connect('button-press-event', self.on_button_press)

        self.set_events(
            self.get_events() |
            Gdk.EventMask.LEAVE_NOTIFY_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK
        )

    def add_pins(self, pins):
        if type(pins) == Pin:
            pins = [pins]

        for pin in pins:
            self.pins.add(pin)

        self.pins.rebalance()

    def on_configure(self, widget, event):
        """
            Initialise our surface where the actual drawing happens.

            When the draw event happens, we paint this surface to the actual
            widget.

            .. seealso PCBWidget.on_draw
        """

        allocation = self.get_allocation()
        self.surface = self.get_window().create_similar_surface(cairo.CONTENT_COLOR,
            allocation.width, allocation.height)

        ratio_x = allocation.width / self.svg_handle.props.width
        ratio_y = allocation.height / self.svg_handle.props.height

        scale = min(ratio_x, ratio_y)

        ctx = cairo.Context(self.surface)
        ctx.scale(scale, scale)
        ctx.set_source_rgb(1/255, 146/255, 62/255)
        ctx.paint()
        self.svg_handle.render_cairo(ctx)

        return True

    def on_motion_notify(self, widget, event):
        # Convert mouse x and y to coordinates relative to the original SVG size
        allocation = widget.get_allocation()
        ratio_x = self.svg_handle.props.width / allocation.width
        ratio_y = self.svg_handle.props.height / allocation.height

        scale = max(ratio_x, ratio_y)

        scaled_x = event.x * scale
        scaled_y = event.y * scale

        # Inkscape places the point (0, 0) in the bottom left corner
        # instead of the top left corner, so we invert the Y coordinate
        scaled_y = self.svg_handle.props.height - scaled_y

        # Find the nearest pins close to the mouse
        result = self.pins.search_nn((scaled_x, scaled_y))
        if result:
            nearest_pin = result[0].data

            dist = math.sqrt((nearest_pin.x - scaled_x)**2 +
                (nearest_pin.y - scaled_y)**2)

            self.points_to_highlight = []
            if dist <= 5:
                self.points_to_highlight = [nearest_pin]

    def on_button_press(self, widget, event):
        pass

    def on_draw(self, widget, ctx):
        if not self.surface:
            return False

        ctx.set_source_surface(self.surface, 0, 0)
        ctx.paint()

        #for point in self.points_to_highlight:
        #    ctx.save()
        #    ctx.translate(point.x, point.y)
        #    ctx.arc(point.x, point.y, 5, 0, 2*math.pi)
        #    ctx.set_source_rgb(0xFFFF, 0, 0)
        #    ctx.fill()
        #    ctx.restore()


        return False


