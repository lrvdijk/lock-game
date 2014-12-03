import threading
import argparse

from gi.repository import GObject

def run_threaded(function):
    def f(*args, **kwargs):
        thread = threading.Thread(target=function, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()

    return f

class BaseCommand(GObject.GObject):
    __gsignals__ = {
        'command-output': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'command-done': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def output_line(self, text):
        self.emit("{}\n".format(text))

    def help(self):
        return ""

class HelpCommand(BaseCommand):
    """
        help
        ====

        Prints the available commands
    """

    program_name = "help"
    hide = False

    @run_threaded
    def run(self, shell_manager, command_string):
        self.output_line("Available programs:")

        for command in shell_manager.commands.values():
            self.output_line(command.program_name)

        self.emit('command-done')

class LsCommand(BaseCommand):
    """
        ls
        ==

        Lists available files and directories in the current or given path.
    """

    program_name = "ls"
    hide = False

    def __init__(self):
        self.parser = argparse.ArgumentParser(self.program_name,
            description="List available files and directories")

        self.parser.add_argument('path', nargs='?', default=".", help="Path to view")
        self.parser.add_argument('-l', '--list', action="store_true", default=False,
            help="Display in list mode")

    @run_threaded
    def run(self, shell_manager, command_string):
        args = self.parser.parse_args(command_string.split()[1:])

        files = shell_manager.get_files(args.path)

        if args.list:
            for file in files:
                self.output_line(file)
        else:
            buffer = ''
            for file in files:
                if len(buffer) + len(file) + 1 > 80:
                    self.output_line(buffer)
                    buffer = file
                else:
                    buffer += ' {}'.format(file)

            self.output_line(buffer)





