#!/usr/bin/env python3
import readline, shlex
from pathlib import Path
from classes.commands import CommandHandler
from classes.utils import HISTFILE

class FileManagerCLI:
    def __init__(self, workspace: Path = Path("/home/user")):
        self.workspace = workspace
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.cmd_handler = CommandHandler(self)
        self.setup_readline()

    def setup_readline(self):
        readline.set_completer_delims(" \t\n\"'`@#$%^&*()-=+[{]}\\|;:,<>?")
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.complete)

        try:
            readline.read_history_file(HISTFILE)
        except FileNotFoundError:
            pass

    def complete(self, text, state):
        return self.cmd_handler.complete(text, state)

    def run(self):
        print("Console File Manager ready. Type 'help' for commands.")
        try:
            while True:
                try:
                    line = input(f"{Path.cwd()}> ")
                except EOFError:
                    print()
                    break
                except KeyboardInterrupt:
                    print()
                    continue
                self.cmd_handler.execute(line)
        finally:
            try:
                readline.write_history_file(HISTFILE)
            except Exception:
                pass
