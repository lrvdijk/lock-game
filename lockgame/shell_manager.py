import os
import zipfile
import shutil
from pathlib import PurePath, Path

from lockgame.config import USER_PATH, DATA_PATH

class ShellManager:
    """
        Manages the available commands for the shell
    """

    def __init__(self, shellname="zsh", user="", host=""):
        self.commands = {}

        self.shellname = shellname
        self.user = user
        self.host = host

        self.cwd = PurePath("/")

        self.base_path = Path(os.path.join(USER_PATH, self.host))

        if not os.path.isdir(str(self.base_path)):
            self.base_path.mkdir(parents=True)
            self.create_initial_state()

    def create_initial_state(self, remove_existing_content=False):
        if remove_existing_content:
            shutil.rmtree(str(self.base_path))
            self.base_path.mkdir(parents=True)

        initial_state_file = os.path.join(DATA_PATH, "{}.zip".format(self.host))
        if os.path.isfile(initial_state_file):
            with zipfile.ZipFile(initial_state_file) as z:
                z.extractall(str(self.base_path))

    @property
    def prompt(self):
        return "{}@{}{}> ".format(self.user, self.host, str(self.cwd))

    def add_command(self, command):
        self.commands[command.program_name] = command

    def find_command(self, command_string):
        parts = command_string.split()

        if not parts[0] in self.commands:
            return None
        else:
            return self.commands[parts[0]]

    def get_absolute_path(self, path, with_base=False):
        path = PurePath(path)

        try:
            new_path = None
            if path.is_absolute():
                new_path = self.base_path / path.relative_to('/')
            else:
                new_path = self.base_path / self.cwd.relative_to('/') / path

            if new_path.exists():
                new_path = new_path.resolve()
        except ValueError:
            new_path = None

        if new_path:
            if with_base:
                return str(new_path)
            else:
                return str(PurePath('/') / new_path.relative_to(self.base_path))

        return None

    def change_directory(self, path):
        absolute_path = Path(self.get_absolute_path(path, True))

        if absolute_path.is_dir():
            self.cwd = PurePath('/') / absolute_path.relative_to(self.base_path)
            return True

        return False

    def get_files(self, path):
        path = PurePath(path)

        try:
            actual_path = self.base_path / self.cwd.relative_to('/') / path
            actual_path = actual_path.resolve()
            actual_path.relative_to(self.base_path)
        except ValueError:
            return []
        else:
            return map(str, [
                child.relative_to(self.base_path / actual_path)
                for child in actual_path.glob('*')
            ])




