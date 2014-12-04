import os
import shutil
import time
import webbrowser

from lockgame.config import DATA_PATH
from lockgame.commands.base import run_threaded, BaseCommand, ShellArgumentParser

class BrowserCommand(BaseCommand):
    program_name = "browser"
    hide = False

    def __init__(self, game_manager):
        BaseCommand.__init__(self)

        self.game_manager = game_manager

        self.parser = ShellArgumentParser(self,
            description="Open the browser")

        self.parser.add_argument('uri', nargs='?', default="",
            help="The URI to open in the browser.")

    @run_threaded
    def run(self, shell_manager, command_string):
        args = self.parser.parse_args(command_string.split()[1:])

        if args.uri.startswith('http'):
            webbrowser.open(args.uri)
        else:
            path = shell_manager.get_absolute_path(args.uri)

            movies = {
                '/home/dorus/jonko.html':
                    'https://www.youtube.com/watch?v=OfBTS4OE-rs',
            }

            if path in movies:
                webbrowser.open(movies[path])
            else:
                self.game_manager.open_troll_video()

        self.emit('command-done')

class JTAGCommand(BaseCommand):
    program_name = "jtag"
    hide = False

    def __init__(self, game_manager):
        BaseCommand.__init__(self)

        self.game_manager = game_manager
        self.parser = ShellArgumentParser(self,
            description="Perform several operations on a connected device"
                        "through JTAG")

        subparsers = self.parser.add_subparsers()

        parser_read = subparsers.add_parser('read', command=self,
            help="Read memory from the device.")
        parser_read.add_argument('file', help="Output filename")
        parser_read.set_defaults(mode="read")

        parser_write = subparsers.add_parser('write', command=self,
            help="Write firmware to the device.")
        parser_write.add_argument('file', help="Input filename")
        parser_write.set_defaults(mode="write")

        parser_shell = subparsers.add_parser('shell', command=self,
            help="Start a shell on the device")
        parser_shell.set_defaults(mode="shell")

    @run_threaded
    def run(self, shell_manager, command_string):
        args = self.parser.parse_args(command_string.split()[1:])

        mode = args.mode if hasattr(args, 'mode') else ""

        self.writeline("Initializing...")
        time.sleep(0.5)
        if self.game_manager.lock_disabled:
            time.sleep(1)
            self.writeline("The device is not responding.")
            self.game_manager.open_troll_video()
        else:
            if mode == 'write':
                self.writeline(
                    "Error: the connected device is in read only mode.")
            elif mode == 'read':
                self.writeline('Reading firmware from device...')
                time.sleep(1.5)
                self.writeline('Decompiling firmware...')
                time.sleep(3)

                self.writeline('Done!')
                shutil.copyfile(
                    os.path.join(DATA_PATH, 'avr_src.c'),
                    shell_manager.get_absolute_path(args.file, True)
                )
            elif mode == 'shell':
                self.game_manager.change_shell(self.game_manager.lock_shell)

        self.emit('command-done')

