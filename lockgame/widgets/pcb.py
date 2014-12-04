import math

from gi.repository import Gtk, Gdk, Rsvg, GObject
import kdtree
import cairo

from lockgame.vector import Vec2d

HIGHLIGHT_RADIUS = 7.5

class WeightedQuickUnion:
    """
        Implements union find algorithm, based on quick find
    """

    def __init__(self, nodes):
        self.nodes = nodes
        self.sizes = {}

        for node in self.nodes:
            self.sizes[node] = 1

    def find(self, p):
        while p != self.nodes[p]:
            p = self.nodes[p]

        return p

    def union(self, p, q):
        i = self.find(p)
        j = self.find(q)

        if i == j:
            return

        if self.sizes[i] < self.sizes[j]:
            self.nodes[i] = j
            self.sizes[j] += self.sizes[i]
        else:
            self.nodes[j] = i
            self.sizes[i] += self.sizes[j]

    def connected(self, p, q):
        return self.find(p) == self.find(q)

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

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __len__(self):
        return 2

class PinManager(GObject.GObject):
    __gsignals__ = {
        'connection-change': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, svg_file, pins):
        GObject.GObject.__init__(self)

        self.svg_handle = Rsvg.Handle.new_from_file(svg_file)

        self.pins = kdtree.create(dimensions=2)
        self.connections = []
        self.quick_union = None

        self.add_pins(pins)

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

        # Create quick union datastructure
        self.quick_union = WeightedQuickUnion({
            pin.data.node: pin.data.node for pin in self.pins.inorder()})

    def add_connection(self, pin1, pin2):
        self.connections.append((pin1, pin2))

        self.quick_union.union(pin1.node, pin2.node)
        self.emit('connection-change')

    def remove_connections(self, pin):
        copy = self.connections

        for connection in copy:
            if connection[0] == pin or connection[1] == pin:
                self.connections.remove(connection)

        # Unfortunately we have to recreate the whole union find structure here
        # again
        self.quick_union = WeightedQuickUnion({
            pin.data.node: pin.data.node for pin in self.pins.inorder()})

        for pin1, pin2 in self.connections:
            self.quick_union.union(pin1.node, pin2.node)

        self.emit('connection-change')

    def pins_connected(self, pin1, pin2):
        return self.quick_union.connected(pin1.node, pin2.node)

    def nodes_connected(self, node1, node2):
        return self.quick_union.connected(node1, node2)

    def nearest_pin(self, point):
        result = self.pins.search_nn(point)

        if result:
            return result[0].data
        else:
            None

class PCBWidget(Gtk.DrawingArea):
    def __init__(self, pin_manager, *args, **kwargs):
        Gtk.DrawingArea.__init__(self, *args, **kwargs)

        self.pin_manager = pin_manager

        self.scale = 1.0
        self.surface = None
        self.wire_surface = None
        self.new_wire_surface = None
        self.highlight_surface = None

        self.points_to_highlight = []
        self.highlighted_pins = []
        self.new_wire_start = None

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

    def to_svg_coordinates(self, x, y):
        allocation = self.get_allocation()
        ratio_x = self.pin_manager.svg_handle.props.width / allocation.width
        ratio_y = self.pin_manager.svg_handle.props.height / allocation.height

        scale = max(ratio_x, ratio_y)

        return scale * x, scale * y

    def to_window_coordinates(self, x, y):
        allocation = self.get_allocation()
        ratio_x = allocation.width / self.pin_manager.svg_handle.props.width
        ratio_y = allocation.height / self.pin_manager.svg_handle.props.height

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

    def start_draw_wire(self, pin, event):
        self.new_wire_start = pin

    def invalidate_new_wire(self, event):
        scaled_x, scaled_y = self.to_svg_coordinates(event.x, event.y)

        # Determine minimum point and maximum point
        min_x = min(scaled_x, self.new_wire_start.x)
        min_y = min(scaled_y, self.new_wire_start.y)

        max_x = max(scaled_x, self.new_wire_start.x)
        max_y = max(scaled_y, self.new_wire_start.y)

        scaled_min_x, scaled_min_y = self.to_window_coordinates(min_x, min_y)
        scaled_max_x, scaled_max_y = self.to_window_coordinates(max_x, max_y)

        update_rect = Gdk.Rectangle()
        update_rect.x = scaled_min_x - 50
        update_rect.y = scaled_min_y - 50
        update_rect.width = (scaled_max_x - scaled_min_x) + 100
        update_rect.height = (scaled_max_y - scaled_min_y) + 100

        # paint to the surface where we store our state
        cairo_ctx = cairo.Context(self.new_wire_surface)

        # Clear previous contents
        cairo_ctx.set_source_rgba(1, 1, 1, 1)
        cairo_ctx.set_operator(cairo.OPERATOR_CLEAR)

        Gdk.cairo_rectangle(cairo_ctx, update_rect)
        cairo_ctx.fill()

        self.get_window().invalidate_rect(update_rect, False)

    def update_new_wire(self, event):
        if not self.new_wire_start:
            return

        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            self.invalidate_new_wire(event)
            self.draw_new_wire(event)

    def draw_new_wire(self, event):
        if not self.new_wire_start:
            return

        scaled_x, scaled_y = self.to_svg_coordinates(event.x, event.y)
        self.draw_wire(self.new_wire_start.as_vector(), Vec2d(scaled_x, scaled_y),
            self.new_wire_surface, color=0xFF9900)

    def draw_wire(self, vec1, vec2, surface, color=0x0066FF):
        ctx = cairo.Context(surface)

        scaled_x1, scaled_y1 = self.to_window_coordinates(vec1.x, vec1.y)
        scaled_x2, scaled_y2 = self.to_window_coordinates(vec2.x, vec2.y)

        v1 = Vec2d(scaled_x1, scaled_y1)
        v2 = Vec2d(scaled_x2, scaled_y2)

        # Move to starting point
        ctx.move_to(scaled_x1, scaled_y1)

        # Vector point from start to end, which is the direction vector
        v = (v2 - v1)
        v_norm = v.normalized()

        # Traverse the vector a bit for a good position of the first
        # control point of the curve
        contr1_start = v1 + (v_norm * (v.length / 4))
        contr1_perp = contr1_start.perpendicular().normalized()
        contr1_point = contr1_start + (contr1_perp * (v.length / 4))

        # The same, but then for the other side
        contr2_start = v2 - (v_norm * ((v.length) / 4))
        contr2_perp = -contr2_start.perpendicular().normalized()
        contr2_point = contr2_start + (contr2_perp * (v.length / 4))

        ctx.curve_to(contr1_point.x, contr1_point.y, contr2_point.x, contr2_point.y,
            v2.x, v2.y)

        ctx.set_source_rgb((color >> 16)/255, ((color & 0xFF00) >> 8)/255,
            (color & 0xFF)/255)
        ctx.set_line_width(5)
        ctx.stroke()

    def draw_connections(self):
        self.create_wire_surface()

        for connection in self.pin_manager.connections:
            color = 0xFFDD55
            if connection[0].node == 'GND' or connection[1].node == 'GND':
                color = 0x0066FF
            elif connection[0].node == 'VCC' or connection[1].node == 'VCC':
                color = 0xFF0000

            self.draw_wire(connection[0], connection[1], self.wire_surface, color)

        self.queue_draw()

    def on_configure(self, widget, event):
        """
            Initialise our surface where the actual drawing happens.

            When the draw event happens, we paint this surface to the actual
            widget.

            We have separate surfaces for highlighting pins, new wires, and
            existing connections.

            .. seealso PCBWidget.on_draw
        """

        allocation = self.get_allocation()

        # Create a surface where we will draw our PCB SVG
        self.surface = self.get_window().create_similar_surface(cairo.CONTENT_COLOR,
            allocation.width, allocation.height)

        # Scale our svg to the widget size
        ratio_x = allocation.width / self.pin_manager.svg_handle.props.width
        ratio_y = allocation.height / self.pin_manager.svg_handle.props.height

        self.scale = min(ratio_x, ratio_y)

        ctx = cairo.Context(self.surface)
        ctx.scale(self.scale, self.scale)
        ctx.set_source_rgb(1/255, 146/255, 62/255)
        ctx.paint()
        self.pin_manager.svg_handle.render_cairo(ctx)

        self.create_highlight_surface()
        self.create_new_wire_surface()
        self.draw_connections()

        return True

    def create_highlight_surface(self):
        """
            A surface where we draw pin highlights.

            Gets completely redrawn on window resize.
            Gets partially redrawn when the user moves the mouse.
        """

        allocation = self.get_allocation()

        # Create a separate surface for highlighting areas
        self.highlight_surface = self.get_window().create_similar_surface(
            cairo.CONTENT_COLOR_ALPHA, allocation.width, allocation.height)

        highlight_ctx = cairo.Context(self.highlight_surface)

        # Make sure it is completely transparent
        highlight_ctx.set_source_rgba(1, 1, 1, 0)
        highlight_ctx.set_operator(cairo.OPERATOR_SOURCE)
        highlight_ctx.paint()

    def create_wire_surface(self):
        """
            The surface where all connections between pins are drawn.

            This surface is completely redrawn every time a new connection
            is made.
        """
        allocation = self.get_allocation()

        # And another surface for the wires
        self.wire_surface = self.get_window().create_similar_surface(
            cairo.CONTENT_COLOR_ALPHA, allocation.width, allocation.height)

        wire_ctx = cairo.Context(self.wire_surface)
        wire_ctx.set_source_rgba(1, 1, 1, 0)
        wire_ctx.set_operator(cairo.OPERATOR_SOURCE)
        wire_ctx.paint()

    def create_new_wire_surface(self):
        """
            This surface is used for drawing a wire when the user wants to make
            a new connection.

            It only gets partially redrawn when the user moves the mouse.
        """
        allocation = self.get_allocation()

        # And another surface for the wires
        self.new_wire_surface = self.get_window().create_similar_surface(
            cairo.CONTENT_COLOR_ALPHA, allocation.width, allocation.height)

        wire_ctx = cairo.Context(self.new_wire_surface)
        wire_ctx.set_source_rgba(1, 1, 1, 0)
        wire_ctx.set_operator(cairo.OPERATOR_SOURCE)
        wire_ctx.paint()

    def on_motion_notify(self, widget, event):
        # Convert mouse x and y to coordinates relative to the original SVG size
        scaled_x, scaled_y = self.to_svg_coordinates(event.x, event.y)

        # Find the nearest pins close to the mouse
        nearest_pin = self.pin_manager.nearest_pin((scaled_x, scaled_y))
        if nearest_pin:
            dist = math.sqrt((nearest_pin.x - scaled_x)**2 +
                (nearest_pin.y - scaled_y)**2)

            while self.highlighted_pins:
                pin = self.highlighted_pins.pop()
                self.unhighlight_pin(pin)

            if dist <= 5:
                if nearest_pin not in self.highlighted_pins:
                    self.highlight_pin(nearest_pin)

                if event.state & Gdk.ModifierType.BUTTON1_MASK:
                    # Button pressed
                    if not self.new_wire_start:
                        self.start_draw_wire(nearest_pin, event)

        self.update_new_wire(event)

    def on_button_release(self, widget, event):
        svg_x, svg_y = self.to_svg_coordinates(event.x, event.y)
        nearest_pin = self.pin_manager.nearest_pin((svg_x, svg_y))
        dist = 0

        if nearest_pin:
            dist = math.sqrt((nearest_pin.x - svg_x)**2 +
                (nearest_pin.y - svg_y)**2)

        if self.new_wire_start:
            # Check if we need to make a new connection
            if nearest_pin and nearest_pin is not self.new_wire_start:
                if dist <= 5:
                    self.pin_manager.add_connection(self.new_wire_start, nearest_pin)
                    self.draw_connections()

            self.invalidate_new_wire(event)

        if event.state & Gdk.ModifierType.BUTTON3_MASK:
            if nearest_pin and dist <= 5:
                self.pin_manager.remove_connections(nearest_pin)
                self.draw_connections()

        self.new_wire_start = None

    def on_draw(self, widget, ctx):
        if not self.surface:
            return False

        ctx.set_source_surface(self.surface, 0, 0)
        ctx.paint()

        if self.wire_surface:
            ctx.set_source_surface(self.wire_surface, 0, 0)
            ctx.paint()

        if self.new_wire_surface:
            ctx.set_source_surface(self.new_wire_surface, 0, 0)
            ctx.paint()

        if self.highlight_surface:
            ctx.set_source_surface(self.highlight_surface, 0, 0)
            ctx.paint()

        return False


