import os

from gi.repository import Gtk

from lockgame.pcb import PCBWidget, Pin

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

        # Set up pins
        pins = [
            # Start with GND nodes
            Pin(85, 321, 'GND'),
            Pin(165.4, 235.6, 'GND'),
            Pin(185.2, 93.0, 'GND'),
            Pin(289.2, 34.8, 'GND'),

            # VCC
            Pin(165.8, 222.4, 'VCC'),
            Pin(336.75, 34.57, 'VCC'),

            # Atmega16u4 left
            Pin(203, 208.8, 'PE6'),
            Pin(203, 199.3, 'Uvcc'),
            Pin(203, 189.8, 'D-'),
            Pin(203, 180.3, 'D+'),
            Pin(203, 170.8, 'UGnd'),
            Pin(203, 161.3, 'UCap'),
            Pin(203, 151.8, 'VBus'),
            Pin(203, 142.3, 'PB0'),
            Pin(203, 132.8, 'PB1'),
            Pin(203, 123.3, 'PB2'),
            Pin(203, 113.8, 'PB3'),

            # Atmega16u4 bottom
            Pin(215, 100, 'PB7'),
            Pin(224.5, 100, 'RESET'),
            Pin(234, 100, 'VCC'),
            Pin(243.5, 100, 'GND'),
            Pin(253, 100, 'XTAL1'),
            Pin(262.5, 100, 'XTAL2'),
            Pin(272, 100, 'PD0'),
            Pin(281.5, 100, 'PD1'),
            Pin(291, 100, 'PD2'),
            Pin(300.5, 100, 'PD3'),
            Pin(310, 100, 'PD5'),

            # Atmega16u4 right
            Pin(324.5, 208.7, 'PE2'),
            Pin(324.5, 199.2, 'PC7'),
            Pin(324.5, 189.7, 'PC6'),
            Pin(324.5, 180.2, 'PB6'),
            Pin(324.5, 170.7, 'PB5'),
            Pin(324.5, 161.2, 'PB4'),
            Pin(324.5, 151.7, 'PD7'),
            Pin(324.5, 142.2, 'PD6'),
            Pin(324.5, 132.7, 'PD4'),
            Pin(324.5, 123.2, 'AVCC'),
            Pin(324.5, 113.7, 'GND'),

            # Atmega16u4 top
            Pin(217, 221, 'PB7'),
            Pin(226.5, 221, 'RESET'),
            Pin(236, 221, 'VCC'),
            Pin(245.5, 221, 'GND'),
            Pin(255, 221, 'XTAL1'),
            Pin(264.5, 221, 'XTAL2'),
            Pin(274, 221, 'PD0'),
            Pin(283.5, 221, 'PD1'),
            Pin(293, 221, 'PD2'),
            Pin(302.5, 221, 'PD3'),
            Pin(312, 221, 'PD5'),
        ]

        self.pcb.add_pins(pins)
        self.stack.add_titled(self.pcb, "pcb", "PCB View")


