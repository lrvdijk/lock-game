from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Lock hacking")

        self.set_border_width(10)
        self.set_default_size(1024, 768)

        self.hb = Gtk.HeaderBar()
        self.hb.props.show_close_button = True
        self.set_titlebar(self.hb)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(1000)

        self.stack_switch = Gtk.StackSwitcher()
        self.stack_switch.set_stack(self.stack)
        self.hb.props.custom_title = self.stack_switch

        self.stack.add_titled(Gtk.Label("test"), "test1", "Test 1")
        self.stack.add_titled(Gtk.Label("test dfdg"), "test2", "Test 2")

        self.add(self.stack)


