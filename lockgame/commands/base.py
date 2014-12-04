import threading
import argparse

from gi.repository import GObject

def run_threaded(function):
    def f(*args, **kwargs):
        thread = threading.Thread(target=function, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()

    return f

class ShellArgumentParser(argparse.ArgumentParser):
    def __init__(self, command=None, *args, **kwargs):
        self.command = command
        if 'prog' not in kwargs:
            kwargs['prog'] = self.command.program_name

        argparse.ArgumentParser.__init__(self, *args, **kwargs)

    def print_usage(self, file=None):
        argparse.ArgumentParser.print_usage(self, file=self.command)
        self.command.emit('command-done')

    def print_help(self, file=None):
        argparse.ArgumentParser.print_help(self, file=self.command)
        self.command.emit('command-done')

    def _print_message(self, message, file=None):
        argparse.ArgumentParser._print_message(self, message, file=self.command)

class BaseCommand(GObject.GObject):
    __gsignals__ = {
        'command-output': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'command-done': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def write(self, text):
        self.emit('command-output', text)

    def writeline(self, text):
        self.emit('command-output', "{}\n".format(text))

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
        self.writeline("Available programs:")

        for command in shell_manager.commands.values():
            self.writeline(command.program_name)

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
        BaseCommand.__init__(self)
        self.parser = ShellArgumentParser(self,
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
                self.writeline(file)
        else:
            buffer = ''
            for file in files:
                if len(buffer) + len(file) + 1 > 80:
                    self.writeline(buffer.strip())
                    buffer = file
                else:
                    buffer += '{} '.format(file)

            self.writeline(buffer.strip())

        self.emit('command-done')

class CdCommand(BaseCommand):
    """
        cd
        ==

        Change directory
    """

    program_name = "cd"
    hide = False

    def __init__(self):
        BaseCommand.__init__(self)

        self.parser = ShellArgumentParser(self,
            description="Change directory")
        self.parser.add_argument('path', nargs='?', default='.',
            help="The path to change to")

    @run_threaded
    def run(self, shell_manager, command_string):
        args = self.parser.parse_args(command_string.split()[1:])

        shell_manager.change_directory(args.path)

        self.emit('command-done')

