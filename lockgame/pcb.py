import collections

from gi.repository import Gtk, Gdk, Rsvg
import kdtree

Pin = collections.namedtuple('Pin', 'node x y')

class PCBWidget(Gtk.DrawingArea):
    def __init__(self, svg_file, *args, **kwargs):
        Gtk.DrawingArea.__init__(self, *args, **kwargs)

        self.svg_handle = Rsvg.Handle.new_from_file(svg_file)
        self.pins = {}
        self.pin_locations = kdtree.create(dimensions=2)

        self.connect('draw', self.on_draw)

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
            self.pins[(pin.x, pin.y)] = pin
            self.pin_locations.add((pin.x, pin.y))

        self.pin_locations.rebalance()

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

        print(scaled_x, scaled_y)

    def on_button_press(self, widget, event):
        pass

    def on_draw(self, widget, ctx):

        allocation = self.get_allocation()

        self.modify_bg(Gtk.StateFlags.NORMAL, Gdk.Color((1/255)*65536,
            (146/255)*65536, (62/255)*65536))

        ratio_x = allocation.width / self.svg_handle.props.width
        ratio_y = allocation.height / self.svg_handle.props.height

        scale = min(ratio_x, ratio_y)
        ctx.scale(scale, scale)
        self.svg_handle.render_cairo(ctx)






