from gi.repository import Gtk

class ShellWidget(Gtk.ScrolledWindow):
    """
        Custom widget which tries to mimic a simple shell
    """

    def __init__(self, shell_manager, *args, **kwargs):
        Gtk.VBox.__init__(self, *args, **kwargs)

        self.shell_manager = shell_manager

        self.viewport = Gtk.Viewport()
        self.add(self.viewport)

        # Create vbox
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.viewport.add(self.vbox)

        # Create textview
        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.vbox.pack_start(self.textview, True, True, 0)

        # Create command entry widget
        # This contains a label containing the prompt, and the entry itself
        self.entry_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.prompt_label = Gtk.Label("Booting...")
        self.command_entry = Gtk.Entry()

        self.entry_hbox.pack_start(self.prompt_label, False, True, 10)
        self.entry_hbox.pack_start(self.command_entry, True, True, 0)

        self.vbox.pack_start(self.entry_hbox, False, True, 0)
