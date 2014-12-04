import os

from gi.repository import Gtk, Gdk

from lockgame.config import DATA_PATH
from lockgame.widgets import PCBWidget, ShellWidget
from lockgame.game import Game

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Lock hacking")

        self.init_style()

        self.set_name('LockWindow')
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

        self.game_manager = Game()
        self.game_manager.connect('change-shell', self.change_shell)

        self.init_shell_view()
        self.init_pcb_view()

        self.add(self.stack)

    def init_style(self):
        style_provider = Gtk.CssProvider()

        with open(os.path.join(DATA_PATH, "shell.css"), 'rb') as f:
            style_provider.load_from_data(f.read())

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def init_shell_view(self):
        self.shell_widget = ShellWidget(self.game_manager.laptop_shell)
        self.shell_widget.get_style_context().add_class('shell-main')

        self.stack.add_titled(self.shell_widget, "shell", "Shell")

    def init_pcb_view(self):
        self.pcb = PCBWidget(self.game_manager.pin_manager)

        self.stack.add_titled(self.pcb, "pcb", "PCB")

    def change_shell(self, sender, shell):
        self.shell_widget.clear_text()
        self.shell_widget.set_shell_manager(shell)


