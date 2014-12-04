import threading

from gi.repository import Gtk, GLib

class ShellWidget(Gtk.ScrolledWindow):
    """
        Custom widget which tries to mimic a simple shell
    """

    def __init__(self, shell_manager, *args, **kwargs):
        Gtk.VBox.__init__(self, *args, **kwargs)

        self.command_ids = []
        self.output_buffer = ""
        self.output_lock = threading.Lock()

        self.viewport = Gtk.Viewport()
        self.add(self.viewport)

        # Create vbox
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.viewport.add(self.vbox)

        # Create textview
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textbuffer = self.textview.get_buffer()
        self.vbox.pack_start(self.textview, True, True, 0)

        # Create command entry widget
        # This contains a label containing the prompt, and the entry itself
        self.entry_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.prompt_label = Gtk.Label("Booting...")
        self.command_entry = Gtk.Entry()
        self.command_entry.connect('activate', self.run_command)
        self.command_entry.grab_focus()

        self.entry_hbox.pack_start(self.prompt_label, False, True, 10)
        self.entry_hbox.pack_start(self.command_entry, True, True, 0)

        self.vbox.pack_start(self.entry_hbox, False, True, 0)

        self.set_shell_manager(shell_manager)

    def set_shell_manager(self, shell_manager):
        self.shell_manager = shell_manager
        self.prompt_label.set_text(self.shell_manager.prompt)

    def add_text(self, text):
        self.textbuffer.insert(self.textbuffer.get_end_iter(), text)
        adj = self.viewport.get_vadjustment()

        adj.set_value(adj.get_upper())

    def run_command(self, entry):
        command_string = self.command_entry.get_text()
        self.add_text("{}{}\n".format(self.shell_manager.prompt, command_string))

        self.command_entry.set_editable(False)
        self.command_entry.set_text("")

        command = self.shell_manager.find_command(command_string)

        if not command:
            self.add_text("{}: unknown command: {}\n".format(
                self.shell_manager.shellname,
                command_string.split()[0]
            ))

            self.on_command_done(None)
        else:
            # Use idle_add function to prevent threading issues
            # The command.run function is ran in a separate thread
            self.command_ids.append(command.connect('command-output',
                self.on_command_output))

            self.command_ids.append(command.connect('command-done',
                self.on_command_done))

            command.run(self.shell_manager, command_string)

    def on_command_done(self, sender):
        GLib.idle_add(self.update_state, sender)

    def on_command_output(self, sender, text):
        with self.output_lock:
            self.output_buffer += str(text)

        GLib.idle_add(self.write_buffer)

    def write_buffer(self):
        with self.output_lock:
            self.add_text(self.output_buffer)
            self.output_buffer = ''

        return False

    def update_state(self, command):
        self.command_entry.set_editable(True)
        self.remove_listener_ids(command)

        self.prompt_label.set_text(self.shell_manager.prompt)
        self.command_entry.grab_focus()

    def remove_listener_ids(self, command):
        while self.command_ids:
            listener_id = self.command_ids.pop()
            command.disconnect(listener_id)

        return False

    def clear_text(self):
        self.textbuffer.set_text("")


