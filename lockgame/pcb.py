import math

from gi.repository import Gtk, Gdk, Rsvg
import kdtree
import cairo

from lockgame.vector import Vec2d

HIGHLIGHT_RADIUS = 7.5

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

    def as_vector(self):
        return Vec2d(self.x, self.y)

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

        self.scale = 1.0
        self.surface = None
        self.highlight_surface = None
        self.svg_handle = Rsvg.Handle.new_from_file(svg_file)

        self.points_to_highlight = []
        self.pins = kdtree.create(dimensions=2)
        self.highlighted_pins = []

        self.connect('draw', self.on_draw)
        self.connect('configure-event', self.on_configure)

        # Mouse events
        self.connect('motion-notify-event', self.on_motion_notify)
        self.connect('button-release-event', self.on_button_release)

        self.set_events(
            self.get_events() |
            Gdk.EventMask.LEAVE_NOTIFY_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK
        )

    def add_pins(self, pins):
        if type(pins) == Pin:
            pins = [pins]

        for pin in pins:
            # Pin coordinates are given in inkscape coordinates
            # which puts the (0, 0) point in the bottom left corner
            # instead of the top left corner.
            # The line below fixes the y coordinate.
            pin.y = self.svg_handle.props.height - pin.y
            self.pins.add(pin)

        self.pins.rebalance()

    def to_svg_coordinates(self, x, y):
        allocation = self.get_allocation()
        ratio_x = self.svg_handle.props.width / allocation.width
        ratio_y = self.svg_handle.props.height / allocation.height

        scale = max(ratio_x, ratio_y)

        return scale * x, scale * y

    def to_window_coordinates(self, x, y):
        allocation = self.get_allocation()
        ratio_x = allocation.width / self.svg_handle.props.width
        ratio_y = allocation.height / self.svg_handle.props.height

        scale = min(ratio_x, ratio_y)

        return scale * x, scale * y

    def highlight_pin(self, pin):
        ctx = cairo.Context(self.highlight_surface)

        # Convert x and y to window coordinates
        scaled_x, scaled_y = self.to_window_coordinates(pin.x, pin.y)

        ctx.arc(scaled_x, scaled_y, HIGHLIGHT_RADIUS, 0, 2*math.pi)
        ctx.set_source_rgba(1.0, 0, 0, 1.0)
        ctx.fill()

        rect = Gdk.Rectangle()
        rect.x = scaled_x - (HIGHLIGHT_RADIUS + 0.5)
        rect.y = scaled_y - (HIGHLIGHT_RADIUS + 0.5)
        rect.width = (HIGHLIGHT_RADIUS + 0.5) * 2
        rect.height = (HIGHLIGHT_RADIUS + 0.5) * 2

        self.get_window().invalidate_rect(rect, False)
        self.highlighted_pins.append(pin)

    def unhighlight_pin(self, pin):
        ctx = cairo.Context(self.highlight_surface)

        # Convert x and y to window coordinates
        scaled_x, scaled_y = self.to_window_coordinates(pin.x, pin.y)

        ctx.arc(scaled_x, scaled_y, HIGHLIGHT_RADIUS+0.5, 0, 2*math.pi)
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.fill()

        rect = Gdk.Rectangle()
        rect.x = scaled_x - (HIGHLIGHT_RADIUS + 0.5)
        rect.y = scaled_y - (HIGHLIGHT_RADIUS + 0.5)
        rect.width = (HIGHLIGHT_RADIUS + 0.5) * 2
        rect.height = (HIGHLIGHT_RADIUS + 0.5) * 2

        self.get_window().invalidate_rect(rect, False)

    def on_configure(self, widget, event):
        """
            Initialise our surface where the actual drawing happens.

            When the draw event happens, we paint this surface to the actual
            widget.

            We also have a separate surface where we paint highlighted pins, and
            when the user holds the mouse button the new wire.

            .. seealso PCBWidget.on_draw
        """

        allocation = self.get_allocation()

        # Create a surface where we will draw our PCB SVG
        self.surface = self.get_window().create_similar_surface(cairo.CONTENT_COLOR,
            allocation.width, allocation.height)

        # Scale our svg to the widget size
        ratio_x = allocation.width / self.svg_handle.props.width
        ratio_y = allocation.height / self.svg_handle.props.height

        self.scale = min(ratio_x, ratio_y)

        ctx = cairo.Context(self.surface)
        ctx.scale(self.scale, self.scale)
        ctx.set_source_rgb(1/255, 146/255, 62/255)
        ctx.paint()
        self.svg_handle.render_cairo(ctx)

        # Create a separate surface for highlighting areas
        self.highlight_surface = self.get_window().create_similar_surface(
            cairo.CONTENT_COLOR_ALPHA, allocation.width, allocation.height)

        highlight_ctx = cairo.Context(self.highlight_surface)

        # Make sure it is completely transparent
        highlight_ctx.set_source_rgba(1, 1, 1, 0)
        highlight_ctx.set_operator(cairo.OPERATOR_SOURCE)
        highlight_ctx.paint()

        return True

    def on_motion_notify(self, widget, event):
        # Convert mouse x and y to coordinates relative to the original SVG size
        scaled_x, scaled_y = self.to_svg_coordinates(event.x, event.y)

        # Find the nearest pins close to the mouse
        result = self.pins.search_nn((scaled_x, scaled_y))
        if result:
            nearest_pin = result[0].data

            dist = math.sqrt((nearest_pin.x - scaled_x)**2 +
                (nearest_pin.y - scaled_y)**2)

            while self.highlighted_pins:
                pin = self.highlighted_pins.pop()
                self.unhighlight_pin(pin)

            if dist <= 5:
                if nearest_pin not in self.highlighted_pins:
                    self.highlight_pin(nearest_pin)

    def on_button_release(self, widget, event):
        print("Button release")

    def on_draw(self, widget, ctx):
        if not self.surface:
            return False

        ctx.set_source_surface(self.surface, 0, 0)
        ctx.paint()

        if self.highlight_surface:
            ctx.set_source_surface(self.highlight_surface, 0, 0)
            ctx.paint()

        return False


