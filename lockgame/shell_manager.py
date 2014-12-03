
class ShellManager:
    """
        Manages the available commands for the shell
    """

    def __init__(self, user="", host=""):
        self.commands = {}

        self.user = user
        self.host = host

    @property
    def prompt(self):
        return "{}@{}> ".format(self.user, self.host)

    def add_command(self, command):
        self.commands[command.program_name] = command

    def find_command(self, command_string):
        parts = command_string.split()

        if not parts[0] in self.commands:
            return None
        else:
            return self.commands[parts[0]]

