from gi.repository import Gtk, Gdk
import cairo

class PCBWidget(Gtk.DrawingArea):
    def __init__(self, *args, **kwargs):
        Gtk.DrawingArea.__init__(self, *args, **kwargs)

        self.components = {}

    def on_draw(self):
        pass
