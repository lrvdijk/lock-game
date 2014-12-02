import collections

from gi.repository import Gtk, Gdk, Rsvg
import kdtree

Pin = collections.namedtuple('Pin', 'node x y')

class PCBWidget(Gtk.DrawingArea):
    def __init__(self, *args, **kwargs):
        Gtk.DrawingArea.__init__(self, *args, **kwargs)

        self.svg_handle = Rsvg.Handle.new_from_file(svg_file)
        self.connect('draw', self.on_draw)

    def on_draw(self, widget, ctx):

        allocation = self.get_allocation()

        self.modify_bg(Gtk.StateFlags.NORMAL, Gdk.Color((1/255)*65536,
            (146/255)*65536, (62/255)*65536))

        ratio_x = allocation.width / self.svg_handle.props.width
        ratio_y = allocation.height / self.svg_handle.props.height

        scale = min(ratio_x, ratio_y)
        ctx.scale(scale, scale)
        self.svg_handle.render_cairo(ctx)
