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
from pathlib import Path
import readline
from classes.utils import make_abs_path, human_size, pager_lines, HISTFILE


class CommandHandler:
    COMMANDS_LIST = [
        "ls",
        "cd",
        "pwd",
        "cat",
        "head",
        "tail",
        "rm",
        "rmdir",
        "mkdir",
        "touch",
        "cp",
        "mv",
        "rename",
        "search",
        "tree",
        "info",
        "help",
        "preview",
        "edit",
        "clear",
        "cls",
        "echo",
        "history",
        "exit",
        "quit",
        "dir",
        "del",
        "copy",
        "move",
        "ren",
        "export",
        "man",
    ]

    COMMANDS_LIST_HELP = [
        "ls       - ls [-a/-l] [path] ",
        "cd       - cd [dir] ",
        "pwd      - pwd ",
        "cat      - cat [file] ",
        "head     - head [-n N] [file] ",
        "tail     - tail [-n N] [file] ",
        "rm       - rm [file] ",
        "rmdir    - rmdir [directory] ",
        "mkdir    - mkdir [directory] ",
        "touch    - touch [file] ",
        "cp       - cp [source] [dest] ",
        "mv       - mv [source] [dest] ",
        "rename   - rename [options] [pattern] [replacement] [files] ",
        "search   - search [pattern] ",
        "tree     -	tree [path] ",
        "info     - info [command] ",
        "help     - help / ?",
        "preview  - preview [file] ",
        "edit     - edit [file] ",
        "clear    - clear ",
        "cls      - cls ",
        "echo     - echo [text] ",
        "history  - history ",
        "exit     - exit ",
        "quit     - quit ",
        "dir      - dir ",
        "del      - del [file]",
        "copy     - copy [source] [dest] ",
        "move     - move [source] [dest]",
        "ren      - ren [pattern] [replacement] [files] ",
        "export   - export VAR=value ",
        "man      - man [command] ",
    ]

    COMMANDS_LIST_MAN = {
        "ls": "to do",
        "cd": "to do",
        "pwd": "to do",
        "cat": "to do",
        "head": "to do",
        "tail": "to do",
        "rm": "to do",
        "rmdir": "to do",
        "mkdir": "to do",
        "touch": "to do",
        "cp": "to do",
        "mv": "to do",
        "rename": "to do",
        "search": "to do",
        "tree": "to do",
        "info": "to do",
        "help": "to do",
        "preview": "to do",
        "edit": "to do",
        "clear": "to do",
        "cls": "to do",
        "echo": "to do",
        "history": "to do",
        "exit": "to do",
        "quit": "to do",
        "dir": "to do",
        "del": "to do",
        "copy": "to do",
        "move": "to do",
        "ren": "to do",
        "export": "to do",
        "man": "Realy! Are you serious",
    }

    PATH_LIKE = {
        "ls",
        "cd",
        "cat",
        "head",
        "tail",
        "rm",
        "rmdir",
        "mkdir",
        "touch",
        "cp",
        "mv",
        "rename",
        "search",
        "tree",
        "info",
        "preview",
        "edit",
    }

    def __init__(self, cli):
        self.cli = cli

    # -------------------------------
    # Tab Completion
    # -------------------------------
    def complete(self, text, state):
        buffer = readline.get_line_buffer()
        begidx = readline.get_begidx()
        tokens = []
        try:
            tokens = shlex.split(buffer[:begidx])
        except Exception:
            pass
        if not tokens:
            options = [c for c in self.COMMANDS_LIST if c.startswith(text)]
            return options[state] if state < len(options) else None
        cmd = tokens[0]
        if cmd in self.PATH_LIKE:
            return self.path_completions(text, state)
        options = [c for c in self.COMMANDS_LIST if c.startswith(text)]
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
            args = shlex.split(line)
        except Exception as e:
            print("Parse error:", e)
            return
        cmd = args[0]
        if cmd == "?":
            self.cmd_help(args)
        else:
            func = getattr(self, f"cmd_{cmd}", None)
            if func:
                func(args[1:])
            else:
                print("Unknown command:", cmd)

    # -------------------------------
    # Commands
    # -------------------------------
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

    def cmd_cd(self, args):
        target = make_abs_path(args[0]) if args else self.cli.workspace
        try:
            os.chdir(target)
        except Exception as e:
            print("cd error:", e)

    def cmd_pwd(self, args):
        print(Path.cwd())

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

    def cmd_help(self, args):
        print("Available commands:")

        for cmd in self.COMMANDS_LIST_HELP:
            print(f" - {cmd}")

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

    def cmd_edit(self, args):
        if not args:
            print("Usage: edit <file>")
            return
        path = make_abs_path(args[0])
        path.parent.mkdir(parents=True, exist_ok=True)
        editor = (
            os.environ.get("EDITOR")
            or os.environ.get("VISUAL")
            or ("notepad" if platform.system() == "Windows" else "nano")
        )
        try:
            subprocess.run([editor, str(path)])
        except Exception as e:
            print("edit error:", e)

    def cmd_clear(self, args):
        os.system("cls" if os.name == "nt" else "clear")

    def cmd_cls(self, args):
        self.cmd_clear(args)

    def cmd_echo(self, args):
        print(" ".join(args))

    def cmd_history(self, args):
        for i in range(1, readline.get_current_history_length() + 1):
            print(f"{i:4}: {readline.get_history_item(i)}")

    def cmd_exit(self, args):
        sys.exit(0)

    def cmd_quit(self, args):
        sys.exit(0)

    def cmd_dir(self, args):
        self.cmd_ls(args)

    def cmd_del(self, args):
        self.cmd_rm(args)

    def cmd_copy(self, args):
        self.cmd_cp(args)

    def cmd_move(self, args):
        self.cmd_mv(args)

    def cmd_ren(self, args):
        self.cmd_rename(args)

    def cmd_export(self, args):
        if not args:
            print("Usage: export <zip|tar|tar.gz>")
            return

        # User provides extension only
        user_ext = args[0].lower()

        # Normalize extension
        if user_ext in ("zip", ".zip"):
            ext = ".zip"
        elif user_ext in ("tar", ".tar"):
            ext = ".tar"
        elif user_ext in ("gz", "tgz", "tar.gz", ".tar.gz", ".tgz"):
            ext = ".tar.gz"
        else:
            print("Unsupported format. Use zip, tar, or tar.gz")
            return

        # Timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Final output name (always 'data_timestamp.ext')
        final_name = f"data_{timestamp}{ext}"

        out_file = Path("/workspace/exports") / final_name
        workspace = self.cli.workspace
        out_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # ZIP
            if ext == ".zip":
                import zipfile
                with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zf:
                    for f in workspace.rglob("*"):
                        zf.write(f, f.relative_to(workspace))

            # TAR or TAR.GZ
            else:
                import tarfile
                mode = "w:gz" if ext == ".tar.gz" else "w"
                with tarfile.open(out_file, mode) as tf:
                    tf.add(workspace, arcname=workspace.name)

            print(f"Workspace exported to {out_file}")

        except Exception as e:
            print("Export error:", e)
            
    def cmd_man(self, args):
        if not args:
            print("Available commands:")
            for cmd in self.COMMANDS_LIST:
                print(f" - {cmd}")
            print("\nUse 'man <command>' to learn more about a specific command.")
        else:
            cmd_name = args[0]
            if cmd_name in self.COMMANDS_LIST_MAN:
                print(f"Manual for '{cmd_name}':\n")
                print(self.COMMANDS_LIST_MAN[cmd_name])
            else:
                print(f"No manual entry for '{cmd_name}'.")
