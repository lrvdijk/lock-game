import time

from lockgame.commands.base import BaseCommand, ShellArgumentParser, run_threaded

class GetCodeCommand(BaseCommand):
    program_name = "getcode"
    hide = False

    def __init__(self, game_manager):
        BaseCommand.__init__(self)
        self.game_manager = game_manager

        self.parser = ShellArgumentParser(self,
            description="Get the current code for the lock")

    @run_threaded
    def run(self, shell_manager, command_string):
        if shell_manager.user == "root":
            self.writeline("Current code is 7331")
        else:
            self.writeline("Permission denied")
            self.game_manager.open_troll_video()

        self.emit('command-done')

class SetCodeCommand(BaseCommand):
    program_name = "setcode"
    hide = False

    def __init__(self, game_manager):
        BaseCommand.__init__(self)
        self.game_manager = game_manager

        self.parser = ShellArgumentParser(self,
            description="Set the current code for the lock")

        self.parser.add_argument('code', type=int,
            help="The new code to set")

    @run_threaded
    def run(self, shell_manager, command_string):
        args = self.parser.parse_args(command_string.split()[1:])

        if shell_manager.user == "root":
            self.writeline("De code {} wordt nu ingesteld...".format(args.code))
            time.sleep(2)
            self.writeline("Hahaha toch niet! Dat moet je lekker zelf doen kut")
        else:
            self.writeline("Permission denied")
            self.game_manager.open_troll_video()

        self.emit('command-done')

class ExitCommand(BaseCommand):
    program_name = "exit"
    hide = False

    def __init__(self, game_manager):
        BaseCommand.__init__(self)
        self.game_manager = game_manager

    @run_threaded
    def run(self, shell_manager, command_string):
        self.game_manager.change_shell(self.game_manager.laptop_shell)
        self.emit('command-done')
