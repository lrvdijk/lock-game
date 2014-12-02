import os

from gi.repository import Gtk

from lockgame.pcb import PCBWidget

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")

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

        self.init_pcb_view()
        self.stack.add_titled(Gtk.Label("test dfdg"), "test2", "Test 2")

        self.add(self.stack)

    def init_pcb_view(self):
        self.pcb = PCBWidget(os.path.join(DATA_PATH, "pcb.svg"))
        self.stack.add_titled(self.pcb, "pcb", "PCB VIew")


