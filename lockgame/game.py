import os
import random
import webbrowser

from gi.repository import GObject, GLib

from lockgame.config import DATA_PATH
from lockgame.widgets.pcb import PinManager, Pin
from lockgame.shell_manager import ShellManager
from lockgame import commands

# Set up pins
PINS = [
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
    Pin(217, 221, 'AVCC'),
    Pin(226.5, 221, 'GND'),
    Pin(236, 221, 'AREF'),
    Pin(245.5, 221, 'PF0'),
    Pin(255, 221, 'PF1'),
    Pin(264.5, 221, 'PF4'),
    Pin(274, 221, 'PF5'),
    Pin(283.5, 221, 'PF6'),
    Pin(293, 221, 'PF7'),
    Pin(302.5, 221, 'GND'),
    Pin(312, 221, 'VCC'),

    # Via near PF5
    Pin(274.18, 241.14, 'PF5'),
    Pin(264.5, 267.25, 'PF5')
]

class Game(GObject.GObject):
    __gsignals__ = {
        'change-shell': (GObject.SIGNAL_RUN_FIRST, None, (ShellManager,))
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        self.pin_manager = PinManager(os.path.join(DATA_PATH, "pcb.svg"), PINS)
        self.pin_manager.connect('connection-change', self.on_change_connection)

        self.laptop_shell = ShellManager("zsh", "dorus", "laptop")
        self.laptop_shell.change_directory("/home/dorus/")
        self.laptop_shell.add_command(commands.HelpCommand())
        self.laptop_shell.add_command(commands.LsCommand())
        self.laptop_shell.add_command(commands.CdCommand())
        self.laptop_shell.add_command(commands.BrowserCommand(self))
        self.laptop_shell.add_command(commands.JTAGCommand(self))

        self.lock_shell = ShellManager("sh", "user", "lock")
        self.lock_shell.add_command(commands.HelpCommand())
        self.lock_shell.add_command(commands.LsCommand())
        self.lock_shell.add_command(commands.CdCommand())
        self.lock_shell.add_command(commands.GetCodeCommand(self))
        self.lock_shell.add_command(commands.SetCodeCommand(self))
        self.lock_shell.add_command(commands.ExitCommand(self))

        self.lock_disabled = False

    def change_shell(self, shell):
        GLib.idle_add(lambda: self.emit('change-shell', shell))

    def on_change_connection(self, sender):
        pb_connected = []
        pb_connected.append(self.pin_manager.nodes_connected('PB0', 'VCC'))
        pb_connected.append(self.pin_manager.nodes_connected('PB1', 'VCC'))
        pb_connected.append(self.pin_manager.nodes_connected('PB2', 'GND'))
        pb_connected.append(self.pin_manager.nodes_connected('PB3', 'VCC'))

        pb_connected.append(self.pin_manager.nodes_connected('PB4', 'VCC'))
        pb_connected.append(self.pin_manager.nodes_connected('PB5', 'GND'))
        pb_connected.append(self.pin_manager.nodes_connected('PB6', 'GND'))

        if all(pb_connected):
            self.lock_shell.user = "root"
        else:
            self.lock_shell.user = "user"

        # Disable lock shell when tampered with JTAG connections
        conditions = []
        conditions.append(self.pin_manager.quick_union.sizes['PF7'] == 1)
        conditions.append(self.pin_manager.quick_union.sizes['PF6'] == 1)
        conditions.append(self.pin_manager.quick_union.sizes['PF5'] == 1)
        conditions.append(self.pin_manager.quick_union.sizes['PF4'] == 1)
        conditions.append(not self.pin_manager.nodes_connected('VCC', 'GND'))

        print(conditions)

        self.lock_disabled = not all(conditions)

        # If VCC and GND are connected show movie
        if self.pin_manager.nodes_connected('VCC', 'GND'):
            webbrowser.open("https://www.youtube.com/watch?v=heE4p5nvjro")

    def open_troll_video(self):
        videos = [
            'http://youtu.be/Gl49r9zkqAA?t=3s',
            'http://youtu.be/c5g1IfWo8XA?t=7s',
            'http://youtu.be/U-R1Jx5-U64?t=4s',
            'http://youtu.be/YeyzxJlahN4',
            'http://youtu.be/Vzpx1MZWaAM?t=44s',
            'http://youtu.be/ROqepn-8dYQ?t=30s',
        ]

        video = random.choice(videos)

        webbrowser.open(video)


