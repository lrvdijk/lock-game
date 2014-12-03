from gi.repository import GObject, GLib

class ShellManager(GObject.GObject):
    """
        Manages the available commands for the shell
    """

    __gsignals__ = {
        'command-output': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'command-done': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, user="", host=""):
        GObject.GObject.__init__(self)
        self.commands = {}

        self.user = user
        self.host = host

    def add_command(self, command):
        self.commands[command.program_name] = command

    def run_command(self, command_string):
        parts = command_string.split()

        if not parts[0] in self.commands:
            self.emit('command-output', 'sh: unknown command\n')
        else:
            command = self.commands[parts[0]]

            listener_id = command.connect('command-output',
                lambda text: GLib.idle_add(
                    lambda: self.emit('command-output', text)
                )
            )

            args = command.parser.parse_args(parts[1:])
            command.run(self, args)

            command.disconnect(listener_id)

        self.emit('command-done')

