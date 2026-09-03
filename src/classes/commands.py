#!/usr/bin/env python3
import os
import shutil
import subprocess
import fnmatch
import platform
import datetime
import stat
import shlex
import zipfile
import sys
import tarfile
import argparse
import code
import runpy
from pathlib import Path
import readline
from classes.utils import make_abs_path, human_size, pager_lines, HISTFILE


def command(help_text="", path_like=False, file_complete=False, aliases=None, man=None):
    def decorator(func):
        func.command_help = help_text
        func.path_like = path_like
        func.file_complete = file_complete
        func.aliases = aliases or {}
        func.man = man
        return func

    return decorator


class CommandHandler:
    @classmethod
    def get_commands(cls):
        return sorted(
            name[4:]
            for name in dir(cls)
            if name.startswith("cmd_") and callable(getattr(cls, name))
        )

    @classmethod
    def get_command_func(cls, command):
        return getattr(cls, f"cmd_{command}", None)

    @classmethod
    def get_aliases(cls):
        aliases = {}

        for command in cls.get_commands():
            func = cls.get_command_func(command)

            for alias, alias_args in getattr(func, "aliases", {}).items():
                aliases[alias] = (command, alias_args)

        return aliases

    @classmethod
    def get_all_commands(cls):
        commands = set(cls.get_commands())
        commands.update(cls.get_aliases())
        return sorted(commands)

    @classmethod
    def get_path_commands(cls):
        commands = set()

        for command in cls.get_commands():
            func = cls.get_command_func(command)

            if getattr(func, "path_like", False):
                commands.add(command)

                for alias in getattr(func, "aliases", {}):
                    commands.add(alias)

        return commands

    @classmethod
    def get_file_complete_commands(cls):
        commands = set()

        for command in cls.get_commands():
            func = cls.get_command_func(command)

            if getattr(func, "file_complete", False):
                commands.add(command)

                for alias in getattr(func, "aliases", {}):
                    commands.add(alias)

        return commands

    @classmethod
    def get_command_help(cls, command):
        aliases = cls.get_aliases()

        # If it's an alias, show the real command's help
        if command in aliases:
            command = aliases[command][0]

        func = cls.get_command_func(command)
        return getattr(func, "command_help", "")

    @classmethod
    def get_man(cls, command):
        aliases = cls.get_aliases()

        if command in aliases:
            command = aliases[command][0]

        func = cls.get_command_func(command)
        return getattr(func, "man", None)

    def __init__(self, cli):
        self.cli = cli

    # -------------------------------
    # Tab Completion
    # -------------------------------
    def complete(self, text, state):
        buffer = readline.get_line_buffer()
        begidx = readline.get_begidx()

        try:
            tokens = shlex.split(buffer[:begidx])
        except Exception:
            tokens = []

        commands = self.get_all_commands()

        # Completing the command itself
        if not tokens:
            options = [c for c in commands if c.startswith(text)]

            return options[state] if state < len(options) else None

        cmd = tokens[0]

        if cmd in self.get_file_complete_commands():
            return self.file_completions(text, state)

        if cmd in self.get_path_commands():
            return self.path_completions(text, state)

        options = [c for c in commands if c.startswith(text)]

        return options[state] if state < len(options) else None

    def path_completions(self, text, state):
        if text == "":
            text = "."
        expanded = os.path.expanduser(text)
        dirname = os.path.dirname(expanded)
        prefix = os.path.basename(expanded)
        try:
            entries = os.listdir(dirname or ".")
        except Exception:
            entries = []
        matches = []
        for e in entries:
            if e.startswith(prefix):
                full = os.path.join(dirname or ".", e)
                display = (
                    os.path.join(os.path.dirname(text), e)
                    if os.path.dirname(text)
                    else e
                )
                if os.path.isdir(full):
                    display += "/"
                matches.append(display)
        matches.sort()
        return matches[state] if state < len(matches) else None

    def file_completions(self, text, state):
        expanded = os.path.expanduser(text)

        # Nothing typed -> current directory
        if not text:
            dirname = "."
            prefix = ""
        else:
            dirname = os.path.dirname(expanded) or "."
            prefix = os.path.basename(expanded)

        try:
            entries = os.listdir(dirname)
        except (OSError, PermissionError):
            entries = []

        matches = []

        for entry in entries:
            if not entry.startswith(prefix):
                continue

            full_path = os.path.join(dirname, entry)

            # Preserve what the user typed
            if os.path.dirname(text):
                display = os.path.join(os.path.dirname(text), entry)
            else:
                display = entry

            # Files
            if os.path.isfile(full_path):
                matches.append(display)

            # Directories
            elif os.path.isdir(full_path):
                matches.append(display + "/")

        matches.sort(key=str.lower)

        return matches[state] if state < len(matches) else None

    # -------------------------------
    # History expansion
    # -------------------------------
    def expand_history(self, line):
        if not line.startswith("!"):
            return line
        hist_len = readline.get_current_history_length()
        if line == "!!":
            if hist_len == 0:
                print("No previous command")
                return ""
            return readline.get_history_item(hist_len)
        if line[1:].isdigit():
            n = int(line[1:])
            if 1 <= n <= hist_len:
                return readline.get_history_item(n)
            else:
                print("No such history item:", n)
                return ""
        return line

    # -------------------------------
    # Execution
    # -------------------------------
    def execute(self, line):
        line = self.expand_history(line)

        if not line.strip():
            return

        try:
            parsed = shlex.split(line)
        except Exception as e:
            print("Parse error:", e)
            return

        if not parsed:
            return

        command_name = parsed[0]
        command_args = parsed[1:]

        if command_name == "?":
            self.cmd_help(command_args)
            return

        # Resolve aliases
        aliases = self.get_aliases()

        if command_name in aliases:
            real_command, alias_args = aliases[command_name]

            # Alias arguments go BEFORE user arguments
            command_args = alias_args + command_args
            command_name = real_command

        func = getattr(self, f"cmd_{command_name}", None)

        if func:
            func(command_args)
        else:
            print("Unknown command:", command_name)

    # -------------------------------
    # Commands
    # -------------------------------
    @command(
        help_text="ls [-a/-l] [path]",
        path_like=True,
        aliases={
            "ll": ["-l"],
            "la": ["-a"],
            "dir": [],
        },
    )
    def cmd_ls(self, args):
        import argparse

        parser = argparse.ArgumentParser(prog="ls", add_help=False)
        parser.add_argument("path", nargs="?", default=".")
        parser.add_argument("-a", action="store_true")
        parser.add_argument("-l", action="store_true")
        try:
            ns = parser.parse_args(args)
        except SystemExit:
            return
        path = make_abs_path(ns.path)
        if not path.exists():
            print("No such path:", path)
            return
        entries = list(path.iterdir())
        if not ns.a:
            entries = [e for e in entries if not e.name.startswith(".")]
        if ns.l:
            for e in sorted(entries, key=lambda x: x.name.lower()):
                st = e.stat()
                mode = stat.filemode(st.st_mode)
                mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime(
                    "%Y-%m-%d %H:%M"
                )
                size = human_size(st.st_size) if e.is_file() else "-"
                print(f"{mode} {size:>8} {mtime} {e.name}")
        else:
            for e in sorted(entries, key=lambda x: x.name.lower()):
                print(e.name + ("/" if e.is_dir() else ""))

    @command(help_text="cd [path]", path_like=True)
    def cmd_cd(self, args):
        target = make_abs_path(args[0]) if args else self.cli.workspace
        try:
            os.chdir(target)
        except Exception as e:
            print("cd error:", e)

    @command(help_text="pwd")
    def cmd_pwd(self, args):
        print(Path.cwd())

    @command(help_text="cat <file>", path_like=True, file_complete=True)
    def cmd_cat(self, args):
        if not args:
            print("Usage: cat <file>")
            return
        path = make_abs_path(args[0])
        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                print(f.read())
        except Exception as e:
            print("cat error:", e)

    @command(help_text="head <file> [-n lines]", path_like=True, file_complete=True)
    def cmd_head(self, args):
        parser = argparse.ArgumentParser(prog="head", add_help=False)
        parser.add_argument("file")
        parser.add_argument("-n", type=int, default=10)
        try:
            ns = parser.parse_args(args)
        except SystemExit:
            return
        path = make_abs_path(ns.file)
        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f):
                    if i >= ns.n:
                        break
                    print(line, end="")
        except Exception as e:
            print("head error:", e)

    @command(help_text="tail <file> [-n lines]", path_like=True, file_complete=True)
    def cmd_tail(self, args):
        parser = argparse.ArgumentParser(prog="tail", add_help=False)
        parser.add_argument("file")
        parser.add_argument("-n", type=int, default=10)
        try:
            ns = parser.parse_args(args)
        except SystemExit:
            return
        path = make_abs_path(ns.file)
        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()[-ns.n :]
                for line in lines:
                    print(line, end="")
        except Exception as e:
            print("tail error:", e)

    @command(help_text="rm <file>", path_like=True, file_complete=True, aliases={"del": ["<file>"]})
    def cmd_rm(self, args):
        if not args:
            print("Usage: rm <file>")
            return
        path = make_abs_path(args[0])
        if not path.exists():
            print("No such file:", path)
            return
        if path.is_dir():
            print("Use rmdir for directories.")
            return
        try:
            path.unlink()
            print("Deleted", path)
        except Exception as e:
            print("rm error:", e)

    @command(help_text="rmdir <dir>", path_like=True)
    def cmd_rmdir(self, args):
        if not args:
            print("Usage: rmdir <dir>")
            return
        path = make_abs_path(args[0])
        if not path.exists():
            print("No such directory:", path)
            return
        try:
            shutil.rmtree(path)
            print("Removed", path)
        except Exception as e:
            print("rmdir error:", e)

    @command(help_text="mkdir <dir>", path_like=True)
    def cmd_mkdir(self, args):
        if not args:
            print("Usage: mkdir <dir>")
            return
        path = make_abs_path(args[0])
        try:
            path.mkdir(parents=True, exist_ok=False)
            print("Created", path)
        except FileExistsError:
            print("Already exists:", path)
        except Exception as e:
            print("mkdir error:", e)

    @command(help_text="touch <file>", path_like=True)
    def cmd_touch(self, args):
        if not args:
            print("Usage: touch <file>")
            return

        name = args[0]

        # Add default .txt if no extension is present
        if "." not in name:
            name += ".txt"

        path = make_abs_path(name)

        try:
            path.touch(exist_ok=True)
            print("Touched", path)
        except Exception as e:
            print("touch error:", e)

    @command(
        help_text="cp <src> <dst>", path_like=True, aliases={"copy": ["<src>", "<dst>"]}
    )
    def cmd_cp(self, args):
        if len(args) < 2:
            print("Usage: cp <src> <dst>")
            return
        src, dst = make_abs_path(args[0]), make_abs_path(args[1])
        try:
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            print("Copied")
        except Exception as e:
            print("cp error:", e)

    @command(
        help_text="mv <src> <dst>", path_like=True, aliases={"move": ["<src>", "<dst>"]}
    )
    def cmd_mv(self, args):
        if len(args) < 2:
            print("Usage: mv <src> <dst>")
            return
        src, dst = make_abs_path(args[0]), make_abs_path(args[1])
        try:
            shutil.move(str(src), str(dst))
            print("Moved")
        except Exception as e:
            print("mv error:", e)

    @command(help_text="rename <old> <new>", path_like=True, aliases={"ren": ["<old>", "<new>"]})
    def cmd_rename(self, args):
        if len(args) < 2:
            print("Usage: rename <old> <new>")
            return
        old, new = make_abs_path(args[0]), make_abs_path(args[1])
        try:
            old.rename(new)
            print("Renamed")
        except Exception as e:
            print("rename error:", e)

    @command(help_text="search <pattern> [path]")
    def cmd_search(self, args):
        if not args:
            print("Usage: search <pattern> [path]")
            return
        pattern = args[0]
        start = make_abs_path(args[1]) if len(args) > 1 else self.cli.workspace
        for root, dirs, files in os.walk(start):
            for name in files + dirs:
                if fnmatch.fnmatch(name, pattern):
                    print(Path(root) / name)

    @command(help_text="tree [path] [depth]", path_like=True)
    def cmd_tree(self, args):
        start = make_abs_path(args[0]) if args else self.cli.workspace
        max_depth = int(args[1]) if len(args) > 1 else 3

        def _tree(p, prefix="", is_last=True, depth=0):
            if depth == 0:
                # Root: no connector
                print(p.name + ("/" if p.is_dir() else ""))
            else:
                connector = "└── " if is_last else "├── "
                print(prefix + connector + p.name + ("/" if p.is_dir() else ""))

            if p.is_dir() and depth < max_depth:
                # Separate dirs and files, both sorted
                entries = list(p.iterdir())
                dirs = sorted(
                    [e for e in entries if e.is_dir()], key=lambda x: x.name.lower()
                )
                files = sorted(
                    [e for e in entries if not e.is_dir()], key=lambda x: x.name.lower()
                )
                ordered = dirs + files

                for i, e in enumerate(ordered):
                    last = i == len(ordered) - 1

                    if depth == 0:
                        # Direct children of root: no leading "│   "
                        new_prefix = ""
                    else:
                        new_prefix = prefix + ("    " if is_last else "│   ")

                    _tree(e, new_prefix, last, depth + 1)

        _tree(start, "", True, 0)

    @command(help_text="info <path>", path_like=True)
    def cmd_info(self, args):
        if not args:
            print("Usage: info <path>")
            return
        path = make_abs_path(args[0])
        try:
            st = path.stat()
            print("Path:", path)
            print("Type:", "Directory" if path.is_dir() else "File")
            print("Size:", human_size(st.st_size))
            print("Permissions:", stat.filemode(st.st_mode))
            print("Modified:", datetime.datetime.fromtimestamp(st.st_mtime))
            print("Created:", datetime.datetime.fromtimestamp(st.st_ctime))
        except Exception as e:
            print("info error:", e)

    @command(help_text="help / ?")
    def cmd_help(self, args):
        print("Available commands:")

        aliases = self.get_aliases()

        for cmd in self.get_commands():
            help_text = self.get_command_help(cmd)

            if help_text:
                print(f" - {help_text}")
            else:
                print(f" - {cmd}")

            cmd_aliases = [
                alias for alias, (target, _) in aliases.items() if target == cmd
            ]

            if cmd_aliases:
                print(f"   aliases: {', '.join(sorted(cmd_aliases))}")

    @command(help_text="preview <file> [lines]", path_like=True, file_complete=True)
    def cmd_preview(self, args):
        if not args:
            print("Usage: preview <file> [lines]")
            return
        path = make_abs_path(args[0])
        n = int(args[1]) if len(args) > 1 else 25
        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                pager_lines(f.readlines(), n)
        except Exception as e:
            print("preview error:", e)

    @command(help_text="edit <file>", path_like=True, file_complete=True)
    def cmd_edit(self, args):
        if not args:
            print("Usage: edit <file>")
            return

        path = make_abs_path(args[0])

        try:
            from classes.editor import TerminalEditor

            editor = TerminalEditor(path)
            editor.run()
        except Exception as e:
            print(f"edit error: {e}")

    @command(help_text="nano <file>", path_like=True, file_complete=True)
    def cmd_nano(self, args):
        self.cmd_edit(args)

    @command(help_text="vim <file>", path_like=True, file_complete=True)
    def cmd_vim(self, args):
        self.cmd_edit(args)

    @command(help_text="vi <file>", path_like=True, file_complete=True)
    def cmd_vi(self, args):
        self.cmd_edit(args)

    @command(help_text="clear screen", aliases={"cls": []})
    def cmd_clear(self, args):
        os.system("cls" if os.name == "nt" else "clear")

    @command(help_text="echo <text>")
    def cmd_echo(self, args):
        print(" ".join(args))

    @command(help_text="history")
    def cmd_history(self, args):
        for i in range(1, readline.get_current_history_length() + 1):
            print(f"{i:4}: {readline.get_history_item(i)}")

    @command(help_text="exit / quit", aliases={"quit": []})
    def cmd_exit(self, args):
        sys.exit(0)

    @command(help_text="export [name] <zip|tar|tar.gz>")
    def cmd_export(self, args):
        if not args:
            print("Usage: export [name] <zip|tar|tar.gz>")
            return

        # --------------------------------------------------------
        # Parse arguments
        # --------------------------------------------------------

        if len(args) == 1:
            # Old syntax: export zip
            user_name = None
            user_ext = args[0].lower()
        else:
            # New syntax: export my_backup zip
            user_name = args[0]
            user_ext = args[1].lower()

        # --------------------------------------------------------
        # Normalize extension
        # --------------------------------------------------------

        if user_ext in ("zip", ".zip"):
            ext = ".zip"
        elif user_ext in ("tar", ".tar"):
            ext = ".tar"
        elif user_ext in ("gz", "tgz", "tar.gz", ".tar.gz", ".tgz"):
            ext = ".tar.gz"
        else:
            print("Unsupported format. Use zip, tar, or tar.gz")
            return

        # --------------------------------------------------------
        # Generate filename
        # --------------------------------------------------------

        from datetime import datetime

        if user_name:
            # Remove an extension if the user included one
            for possible_ext in (".tar.gz", ".tgz", ".zip", ".tar"):
                if user_name.lower().endswith(possible_ext):
                    user_name = user_name[: -len(possible_ext)]
                    break

            final_name = f"{user_name}{ext}"
        else:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            final_name = f"data_{timestamp}{ext}"

        # --------------------------------------------------------
        # Paths
        # --------------------------------------------------------

        out_file = Path("/workspace/exports") / final_name
        workspace = self.cli.workspace

        out_file.parent.mkdir(parents=True, exist_ok=True)

        # --------------------------------------------------------
        # Export
        # --------------------------------------------------------

        try:
            # ZIP
            if ext == ".zip":
                import zipfile

                with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zf:

                    for f in workspace.rglob("*"):
                        if f.is_file():
                            zf.write(f, f.relative_to(workspace))

            # TAR / TAR.GZ
            else:
                import tarfile

                mode = "w:gz" if ext == ".tar.gz" else "w"

                with tarfile.open(out_file, mode) as tf:
                    tf.add(workspace, arcname=workspace.name)

            print(f"Workspace exported to {out_file}")

        except Exception as e:
            print("Export error:", e)

    @command(help_text="import <file>", path_like=True, file_complete=True)
    def cmd_python(self, args):  # Case B: Enter REPL if no arguments
        # ---------- Case A: run python file ----------
        if args:
            first = args[0]
            full_path = self.cli.workspace / first

            if full_path.exists() and full_path.is_file() and full_path.suffix == ".py":
                try:
                    print(f"Running script: {full_path}")
                    runpy.run_path(str(full_path), run_name="__main__")
                except Exception as e:
                    print("Python script error:", e)
                return

            # Case C: evaluate expression / exec
            expr = " ".join(args)
            try:
                result = eval(expr, {}, {})
                if result is not None:
                    print(result)
                return
            except SyntaxError:
                try:
                    exec(expr, {}, {})
                    return
                except Exception as e:
                    print("Python execution error:", e)
                    return
            except Exception as e:
                print("Python evaluation error:", e)
                return

        # ---------- Case B: Interactive REPL ----------
        print("Entering Python shell. Type exit() to leave.\n")

        ctx = {
            "workspace": self.cli.workspace,
            "fm": self,
        }

        buffer = ""
        stdin = sys.__stdin__  # <-- BYPASS CLI history completely

        while True:
            try:
                # manual prompt without history tracking
                prompt = ">>> " if buffer == "" else "... "
                print(prompt, end="", flush=True)

                line = stdin.readline()
                if not line:
                    print("\nExited Python shell.\n")
                    return

                line = line.rstrip("\n")

            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
                buffer = ""
                continue

            # exit command
            if line.strip() in ("exit", "exit()", "quit", "quit()"):
                print("Exited Python shell.\n")
                return

            buffer += line + "\n"

            # Try to compile the buffer
            try:
                code_obj = compile(buffer, "<pyshell>", "single")
            except SyntaxError as e:
                if "unexpected EOF" in str(e):
                    continue
                print(e)
                buffer = ""
                continue

            # Execute
            try:
                exec(code_obj, ctx, ctx)
            except Exception as e:
                print(e)

            buffer = ""

    @command(help_text="man [command]")
    def cmd_man(self, args):
        if not args:
            print("Available commands:")

            for cmd in self.get_all_commands():
                print(f" - {cmd}")

            print("\nUse 'man <command>' to learn more about a specific command.")
            return

        cmd_name = args[0]

        # Resolve aliases first
        aliases = self.get_aliases()

        if cmd_name in aliases:
            cmd_name = aliases[cmd_name][0]

        # Make sure the command actually exists
        if cmd_name not in self.get_commands():
            print(f"No manual entry for '{args[0]}'.")
            return

        # /usr/local/fm/classes
        base_dir = Path(__file__).resolve().parent

        manuals_dir = base_dir / "manuals"

        # Prefer <command>.txt
        man_path = manuals_dir / f"{cmd_name}.txt"

        # Fallback to a file without extension
        if not man_path.exists():
            man_path = manuals_dir / cmd_name

        try:
            with man_path.open("r", encoding="utf-8") as f:
                lines = list(f)

            pager_lines(lines, lines_per_page=25)

        except FileNotFoundError:
            print(f"No manual entry for '{cmd_name}'.")
